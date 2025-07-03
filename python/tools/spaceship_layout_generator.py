import json
import os
import random
import math
import argparse
import importlib.util
from typing import List, Dict, Any

# Try to import SpaceshipLayoutValidator
# First try relative import (when used as part of a package)
try:
    from .spaceship_layout_validator import SpaceshipLayoutValidator
except ImportError:
    # If that fails, try direct import (when run as a script)
    try:
        from spaceship_layout_validator import SpaceshipLayoutValidator
    except ImportError:
        # If both fail, try to import from the same directory
        try:
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Create the full path to the validator module
            validator_path = os.path.join(current_dir, "spaceship_layout_validator.py")
            # Import the module dynamically
            spec = importlib.util.spec_from_file_location("spaceship_layout_validator", validator_path)
            validator_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(validator_module)
            # Get the SpaceshipLayoutValidator class
            SpaceshipLayoutValidator = validator_module.SpaceshipLayoutValidator
        except Exception as e:
            print(f"Warning: Could not import SpaceshipLayoutValidator: {str(e)}")
            print("Layout validation will not be available.")
            # Create a dummy validator class for graceful degradation
            class SpaceshipLayoutValidator:
                def __init__(self, model_name=None):
                    pass
                def validate_layout(self, layout):
                    return {
                        "score": 0.0,
                        "reasoning": "Validation not available: SpaceshipLayoutValidator could not be imported.",
                        "suggestions": "Please ensure the spaceship_layout_validator.py file is in the same directory."
                    }

def load_parts_data(json_path: str) -> List[Dict[str, Any]]:
    """
    Load parts data from the batch_import_analysis.json file.

    Args:
        json_path (str): Path to the batch_import_analysis.json file

    Returns:
        List[Dict[str, Any]]: List of parts with their metadata
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Parts data file not found: {json_path}")

    with open(json_path, 'r') as f:
        parts_data = json.load(f)

    return parts_data

def select_parts_by_size(parts_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Select parts by size_type.

    Args:
        parts_data (List[Dict[str, Any]]): List of parts with their metadata

    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary of parts grouped by size_type
    """
    # Group parts by size_type
    parts_by_size = {
        "Big": [],
        "Medium": [],
        "Small": []
    }

    for part in parts_data:
        size_type = part.get("size_type")
        if size_type in parts_by_size:
            parts_by_size[size_type].append(part)

    return parts_by_size

def generate_spaceship_layout(parts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate a spaceship layout by selecting and positioning parts.

    Args:
        parts_data (List[Dict[str, Any]]): List of parts with their metadata

    Returns:
        List[Dict[str, Any]]: Spaceship layout with positioned parts
    """
    # Group parts by size
    parts_by_size = select_parts_by_size(parts_data)

    # Initialize the layout
    layout = []

    # 1. Select one Big part as the core (placed at [0,0,0])
    if parts_by_size["Big"]:
        core_part = random.choice(parts_by_size["Big"])
        layout.append({
            "name": core_part["name"],
            "position": [0, 0, 0],
            "size_type": "Big",
            "role": "core"
        })
    else:
        print("Warning: No Big parts available for core. Using a Medium part instead.")
        if parts_by_size["Medium"]:
            core_part = random.choice(parts_by_size["Medium"])
            layout.append({
                "name": core_part["name"],
                "position": [0, 0, 0],
                "size_type": "Medium",
                "role": "core"
            })
        else:
            print("Error: No suitable parts for core found.")
            return []

    # 2. Select 2-4 Medium parts as wings or engines
    num_medium_parts = min(random.randint(2, 4), len(parts_by_size["Medium"]))
    medium_parts = random.sample(parts_by_size["Medium"], num_medium_parts)

    # Position medium parts as wings and engines
    for i, part in enumerate(medium_parts):
        if i % 2 == 0:  # Even indices are wings
            # Position wings to the sides
            side = 1 if i % 4 == 0 else -1
            position = [side * 5, 0, 0]
            role = "wing"
        else:  # Odd indices are engines
            # Position engines behind
            position = [0, 0, -5 - (i // 2) * 3]
            role = "engine"

        layout.append({
            "name": part["name"],
            "position": position,
            "size_type": "Medium",
            "role": role
        })

    # 3. Select 2-5 Small parts as details
    num_small_parts = min(random.randint(2, 5), len(parts_by_size["Small"]))
    small_parts = random.sample(parts_by_size["Small"], num_small_parts)

    # Position small parts randomly around the core
    for i, part in enumerate(small_parts):
        # Generate random positions around the core
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(2, 4)
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        y = random.uniform(-1, 1)

        layout.append({
            "name": part["name"],
            "position": [x, y, z],
            "size_type": "Small",
            "role": "detail"
        })

    return layout

def save_layout_to_json(layout: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save the spaceship layout to a JSON file.

    Args:
        layout (List[Dict[str, Any]]): Spaceship layout with positioned parts
        output_path (str): Path to save the output JSON file
    """
    with open(output_path, 'w') as f:
        json.dump(layout, f, indent=2)

    print(f"Spaceship layout saved to: {output_path}")

def validate_spaceship_layout(layout: List[Dict[str, Any]], model_name: str = "microsoft/phi-2") -> Dict[str, Any]:
    """
    Validate a spaceship layout using a local LLM.

    Args:
        layout (List[Dict[str, Any]]): The spaceship layout to validate
        model_name (str): The name or path of the LLM model to use

    Returns:
        Dict[str, Any]: The validation results
    """
    try:
        validator = SpaceshipLayoutValidator(model_name=model_name)
        results = validator.validate_layout(layout)
        return results
    except Exception as e:
        print(f"Error during layout validation: {str(e)}")
        return {
            "score": 0.0,
            "reasoning": "Validation failed due to an error.",
            "suggestions": "Please check the error message and try again.",
            "error": str(e)
        }

def main():
    """
    Main function to generate a spaceship layout and optionally validate it.

    Command-line arguments:
    --input, -i : Path to the batch_import_analysis.json file
    --output, -o : Path to save the output layout JSON file
    --validate, -v : Enable layout validation using a local LLM
    --model, -m : Model to use for validation (default: microsoft/phi-2)

    Examples:
    # Generate a layout without validation
    python spaceship_layout_generator.py

    # Generate a layout and validate it with the default model (Phi-2)
    python spaceship_layout_generator.py --validate

    # Generate a layout and validate it with a specific model
    python spaceship_layout_generator.py --validate --model TinyLlama/TinyLlama-1.1B-Chat-v1.0

    # Specify input and output paths
    python spaceship_layout_generator.py -i my_parts.json -o my_layout.json --validate

    Dependencies for validation:
    - torch
    - transformers

    Install with: pip install torch transformers
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate and validate spaceship layouts")
    parser.add_argument("--input", "-i", help="Path to the batch_import_analysis.json file")
    parser.add_argument("--output", "-o", help="Path to save the output layout JSON file")
    parser.add_argument("--validate", "-v", action="store_true", help="Validate the layout using a local LLM")
    parser.add_argument("--model", "-m", default="microsoft/phi-2", 
                        help="Model to use for validation (default: microsoft/phi-2)")
    args = parser.parse_args()

    # Default paths
    input_path = args.input if args.input else "batch_import_analysis.json"
    output_path = args.output if args.output else "spaceship_layout.json"

    # Check if input file exists in current directory
    if not os.path.exists(input_path):
        # Try to find it in the Houdini project directory
        hip_dir = os.environ.get('HIP', '')
        if hip_dir:
            input_path = os.path.join(hip_dir, "batch_import_analysis.json")
            output_path = os.path.join(hip_dir, "spaceship_layout.json")

    try:
        # Load parts data
        parts_data = load_parts_data(input_path)

        # Generate spaceship layout
        layout = generate_spaceship_layout(parts_data)

        if layout:
            # Save layout to JSON
            save_layout_to_json(layout, output_path)

            # Print summary
            print(f"\nSpaceship Layout Summary:")
            print(f"Core: {sum(1 for part in layout if part['role'] == 'core')} part")
            print(f"Wings: {sum(1 for part in layout if part['role'] == 'wing')} parts")
            print(f"Engines: {sum(1 for part in layout if part['role'] == 'engine')} parts")
            print(f"Details: {sum(1 for part in layout if part['role'] == 'detail')} parts")
            print(f"Total: {len(layout)} parts")

            # Validate the layout if requested
            if args.validate:
                print("\nValidating layout with LLM...")
                validation_results = validate_spaceship_layout(layout, model_name=args.model)

                print(f"\nLayout Validation Results:")
                print(f"Score: {validation_results['score']}/10")
                print(f"Reasoning: {validation_results['reasoning']}")
                print(f"Suggestions: {validation_results['suggestions']}")

                # Save validation results to a separate JSON file
                validation_output_path = os.path.splitext(output_path)[0] + "_validation.json"
                with open(validation_output_path, 'w') as f:
                    json.dump(validation_results, f, indent=2)
                print(f"Validation results saved to: {validation_output_path}")
        else:
            print("Failed to generate spaceship layout.")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
