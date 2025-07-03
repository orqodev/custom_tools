import os
import json
import torch
import sys
from typing import Dict, List, Any, Tuple, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer

class SpaceshipLayoutValidator:
    """
    A class that uses a local LLM to validate and score spaceship layouts.

    This validator loads a lightweight LLM model to evaluate the cohesiveness
    and functionality of procedurally generated spaceship layouts.
    """

    # List of alternative models to try if the primary model fails
    ALTERNATIVE_MODELS = [
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # Smaller model, may have fewer dependencies
        "microsoft/phi-2",                      # Default model
        "facebook/opt-125m"                     # Very small model with minimal dependencies
    ]

    def __init__(self, model_name: str = "microsoft/phi-2"):
        """
        Initialize the SpaceshipLayoutValidator with a specified model.

        Args:
            model_name (str): The name or path of the model to use.
                Default is "microsoft/phi-2" which is a lightweight but capable model.
                Other options include "TinyLlama/TinyLlama-1.1B-Chat-v1.0" or a local path.
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.tried_models = []

        # Try to load the specified model
        self._try_load_model(model_name)

        # If the specified model failed, try alternatives
        if self.model is None:
            self._try_alternative_models()

    def _try_load_model(self, model_name: str) -> bool:
        """
        Try to load a specific model.

        Args:
            model_name (str): The name or path of the model to try loading.

        Returns:
            bool: True if model loaded successfully, False otherwise.
        """
        if model_name in self.tried_models:
            return False

        self.tried_models.append(model_name)

        try:
            print(f"Loading model {model_name} on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name, 
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                trust_remote_code=True
            ).to(self.device)
            print("Model loaded successfully!")
            self.model_name = model_name
            return True
        except ModuleNotFoundError as e:
            if "_bz2" in str(e):
                error_msg = (
                    f"Error: Missing system dependency '_bz2' when loading {model_name}. "
                    f"This is required by the transformers library.\n"
                    f"To fix this, install the bzip2 development libraries:\n"
                    f"- On Ubuntu/Debian: sudo apt-get install libbz2-dev\n"
                    f"- On CentOS/RHEL: sudo yum install bzip2-devel\n"
                    f"- On macOS: brew install bzip2\n"
                    f"Then reinstall Python or create a new environment with Python that includes bz2 support.\n"
                    f"Trying alternative models that may not require bz2..."
                )
                print(error_msg)
                return False
            else:
                print(f"Error loading model {model_name}: {str(e)}")
                return False
        except Exception as e:
            print(f"Error loading model {model_name}: {str(e)}")
            return False

    def _try_alternative_models(self):
        """Try loading alternative models if the primary model failed."""
        for model in self.ALTERNATIVE_MODELS:
            if model not in self.tried_models:
                print(f"Trying alternative model: {model}")
                if self._try_load_model(model):
                    print(f"Successfully loaded alternative model: {model}")
                    return

        print("Failed to load any model. Validation will return default values.")
        # No models could be loaded - validation will use fallback responses

    def _create_prompt(self, layout: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for the LLM based on the spaceship layout.

        Args:
            layout (List[Dict[str, Any]]): The spaceship layout to evaluate.

        Returns:
            str: The formatted prompt for the LLM.
        """
        # Count parts by role
        role_counts = {}
        for part in layout:
            role = part.get("role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1

        role_summary = ", ".join([f"{count} {role}(s)" for role, count in role_counts.items()])

        # Format the layout as a readable string
        layout_str = json.dumps(layout, indent=2)

        prompt = f"""You are a spaceship design expert. Evaluate this 3D spaceship layout for cohesiveness and functionality.

The layout contains {len(layout)} parts: {role_summary}.

Here's the detailed layout with part name, role, position, and size_type:
{layout_str}

Please analyze this layout and:
1. Give a score from 0 to 10 (can include decimals like 7.5) based on:
   - Logical positioning (engines at back, wings on sides, etc.)
   - Balance and symmetry
   - Appropriate use of different sized parts
   - Overall believability as a functional spacecraft

2. Provide brief reasoning for your score.

3. Suggest specific improvements that could make this layout more cohesive or functional.

Format your response exactly like this:
SCORE: [your score]/10
REASONING: [your reasoning]
SUGGESTIONS: [your suggestions]

"""
        return prompt

    def _parse_response(self, response: str) -> Tuple[float, str, str]:
        """
        Parse the LLM response to extract score, reasoning, and suggestions.

        Args:
            response (str): The raw response from the LLM.

        Returns:
            Tuple[float, str, str]: The extracted score, reasoning, and suggestions.
        """
        score = 0.0
        reasoning = ""
        suggestions = ""

        # Extract score
        if "SCORE:" in response:
            score_line = response.split("SCORE:")[1].split("\n")[0].strip()
            try:
                # Extract the numeric part before "/10"
                score = float(score_line.split("/")[0].strip())
            except ValueError:
                print(f"Warning: Could not parse score from '{score_line}'")

        # Extract reasoning
        if "REASONING:" in response:
            reasoning_parts = response.split("REASONING:")[1].split("SUGGESTIONS:")[0].strip()
            reasoning = reasoning_parts

        # Extract suggestions
        if "SUGGESTIONS:" in response:
            suggestions = response.split("SUGGESTIONS:")[1].strip()

        return score, reasoning, suggestions

    def validate_layout(self, layout: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a spaceship layout using the LLM.

        Args:
            layout (List[Dict[str, Any]]): The spaceship layout to validate.

        Returns:
            Dict[str, Any]: A dictionary containing the validation results:
                - score (float): The layout score (0-10)
                - reasoning (str): The reasoning behind the score
                - suggestions (str): Suggestions for improvement
        """
        # Check if model and tokenizer were successfully loaded
        if self.model is None or self.tokenizer is None:
            # Provide a more helpful fallback response with basic layout analysis
            return self._generate_fallback_response(layout)

        try:
            # Create the prompt
            prompt = self._create_prompt(layout)

            # Generate response from the model
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_new_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True
                )

            # Decode the response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract the generated part (after the prompt)
            if prompt in response:
                response = response[len(prompt):].strip()

            # Parse the response
            score, reasoning, suggestions = self._parse_response(response)

            return {
                "score": score,
                "reasoning": reasoning,
                "suggestions": suggestions,
                "raw_response": response,
                "model_used": self.model_name
            }
        except Exception as e:
            error_msg = str(e)
            print(f"Error during validation: {error_msg}")
            return {
                "score": 0.0,
                "reasoning": "Validation failed due to an error.",
                "suggestions": "Please check the error message and try again.",
                "error": error_msg,
                "model_used": self.model_name
            }

    def _generate_fallback_response(self, layout: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a fallback response when no model could be loaded.
        This provides basic layout analysis without using an LLM.

        Args:
            layout (List[Dict[str, Any]]): The spaceship layout to analyze.

        Returns:
            Dict[str, Any]: A basic analysis of the layout.
        """
        # Count parts by role
        role_counts = {}
        for part in layout:
            role = part.get("role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1

        # Basic layout analysis
        has_core = role_counts.get("core", 0) > 0
        has_engines = role_counts.get("engine", 0) > 0
        has_wings = role_counts.get("wing", 0) > 0

        # Calculate a basic score based on presence of essential parts
        score = 5.0  # Start with a neutral score
        if has_core:
            score += 1.0
        if has_engines:
            score += 1.0
        if has_wings:
            score += 1.0

        # Check for balance (equal number of wings on each side)
        wing_positions = [part["position"][0] for part in layout if part.get("role") == "wing"]
        left_wings = sum(1 for pos in wing_positions if pos < 0)
        right_wings = sum(1 for pos in wing_positions if pos > 0)
        if left_wings == right_wings and left_wings > 0:
            score += 1.0

        # Check if engines are at the back
        engine_positions = [part["position"][2] for part in layout if part.get("role") == "engine"]
        if all(pos < 0 for pos in engine_positions) and engine_positions:
            score += 1.0

        # Cap the score at 10
        score = min(score, 10.0)

        # Generate reasoning
        reasoning_parts = []
        if has_core:
            reasoning_parts.append("The layout includes a core component.")
        else:
            reasoning_parts.append("The layout is missing a core component.")

        if has_engines:
            reasoning_parts.append(f"There are {role_counts.get('engine', 0)} engine(s).")
        else:
            reasoning_parts.append("The layout is missing engines.")

        if has_wings:
            reasoning_parts.append(f"There are {role_counts.get('wing', 0)} wing(s).")
        else:
            reasoning_parts.append("The layout is missing wings.")

        if left_wings == right_wings and left_wings > 0:
            reasoning_parts.append("The wings are balanced on both sides.")
        elif has_wings:
            reasoning_parts.append("The wings are not evenly balanced.")

        reasoning = " ".join(reasoning_parts)

        # Generate suggestions
        suggestions_parts = []
        if not has_core:
            suggestions_parts.append("Add a core component at the center of the layout.")
        if not has_engines:
            suggestions_parts.append("Add engines at the back of the spacecraft.")
        if not has_wings:
            suggestions_parts.append("Add wings on both sides for balance.")
        elif left_wings != right_wings:
            suggestions_parts.append("Balance the wings on both sides of the spacecraft.")

        if not suggestions_parts:
            suggestions = "The basic layout looks functional. Consider adding more details or specialized components."
        else:
            suggestions = " ".join(suggestions_parts)

        return {
            "score": score,
            "reasoning": reasoning,
            "suggestions": suggestions,
            "note": "This is a fallback analysis as no LLM model could be loaded. Install required dependencies for more detailed analysis.",
            "tried_models": ", ".join(self.tried_models)
        }

    def suggest_improvements(self, layout: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Suggest improvements to a spaceship layout.

        This is an advanced feature that attempts to have the LLM suggest
        specific changes to the layout, such as repositioning parts or
        swapping components.

        Args:
            layout (List[Dict[str, Any]]): The original spaceship layout.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - improved_layout: A modified layout with suggested improvements
                - changes: A list of changes made to the layout
                - reasoning: The reasoning behind the changes
        """
        # Check if model and tokenizer were successfully loaded
        if self.model is None or self.tokenizer is None:
            # If no model is available, use the fallback mechanism
            fallback_analysis = self._generate_fallback_response(layout)

            # Create a simple improvement based on the fallback analysis
            improved_layout = layout.copy()
            changes = []

            # Apply basic improvements based on fallback analysis
            if "missing a core component" in fallback_analysis["reasoning"]:
                changes.append("Would add a core component at position [0, 0, 0]")

            if "missing engines" in fallback_analysis["reasoning"]:
                changes.append("Would add engines at the back of the spacecraft")

            if "wings are not evenly balanced" in fallback_analysis["reasoning"]:
                changes.append("Would balance wings on both sides")

            return {
                "improved_layout": improved_layout,
                "changes": changes,
                "reasoning": fallback_analysis["reasoning"],
                "note": "This is a fallback suggestion as no LLM model could be loaded. Install required dependencies for more detailed suggestions."
            }

        # This is a placeholder for future implementation with LLM
        # In a full implementation, this would:
        # 1. Create a specialized prompt asking for specific position changes
        # 2. Parse the response to extract position modifications
        # 3. Apply those modifications to create a new layout

        # For now, we'll return the original layout with a note
        return {
            "improved_layout": layout,
            "changes": ["No changes made - this feature is not fully implemented yet"],
            "reasoning": "The suggest_improvements method is a placeholder for future development.",
            "model_used": self.model_name
        }

def main():
    """
    Test the SpaceshipLayoutValidator with a sample layout.
    """
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Validate spaceship layouts using a local LLM")
    parser.add_argument("--input", "-i", default="my_layout.json", 
                        help="Path to the input layout JSON file (default: my_layout.json)")
    parser.add_argument("--output", "-o", default="my_layout_validation.json",
                        help="Path to save the validation results (default: my_layout_validation.json)")
    parser.add_argument("--model", "-m", default="microsoft/phi-2",
                        help="Model to use for validation (default: microsoft/phi-2)")
    parser.add_argument("--suggest", "-s", action="store_true",
                        help="Generate improvement suggestions for the layout")
    args = parser.parse_args()

    # Sample layout for testing if no input file is provided
    sample_layout = [
        {"name": "KB3D_SPS_Hull_B", "role": "core", "position": [0, 0, 0], "size_type": "Big"},
        {"name": "KB3D_SPS_Wings_A", "role": "wing", "position": [5, 0, 0], "size_type": "Medium"},
        {"name": "KB3D_SPS_Wings_A", "role": "wing", "position": [-5, 0, 0], "size_type": "Medium"},
        {"name": "KB3D_SPS_Engine_A", "role": "engine", "position": [0, 0, -5], "size_type": "Medium"}
    ]

    # Load layout from file if it exists
    layout = sample_layout
    try:
        if os.path.exists(args.input):
            print(f"Loading layout from {args.input}")
            with open(args.input, 'r') as f:
                layout = json.load(f)
        else:
            print(f"Input file {args.input} not found, using sample layout")
    except Exception as e:
        print(f"Error loading layout file: {str(e)}")
        print("Using sample layout instead")

    # Initialize the validator with the specified model
    print(f"Initializing validator with model: {args.model}")
    validator = SpaceshipLayoutValidator(model_name=args.model)

    # Validate the layout
    print("Validating layout...")
    result = validator.validate_layout(layout)

    # Print the validation results
    print("\nValidation Results:")
    print(f"Score: {result['score']}/10")
    print(f"Reasoning: {result['reasoning']}")
    print(f"Suggestions: {result['suggestions']}")

    # Check if a model was successfully loaded
    if "model_used" in result:
        print(f"Model used: {result['model_used']}")
    elif "note" in result:
        print(f"Note: {result['note']}")
        print(f"Tried models: {result.get('tried_models', 'None')}")

    # Generate improvement suggestions if requested
    if args.suggest:
        print("\nGenerating improvement suggestions...")
        improvements = validator.suggest_improvements(layout)

        print("\nImprovement Suggestions:")
        print(f"Reasoning: {improvements.get('reasoning', 'None')}")
        print("Changes:")
        for change in improvements.get('changes', []):
            print(f"- {change}")

        if "note" in improvements:
            print(f"Note: {improvements['note']}")

        # Add improvements to the result
        result["improvements"] = improvements

    # Save the validation results to a JSON file
    try:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nValidation results saved to: {args.output}")
    except Exception as e:
        print(f"Error saving validation results: {str(e)}")

if __name__ == "__main__":
    main()
