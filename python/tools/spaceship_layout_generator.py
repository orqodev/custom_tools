import json
import os
import random
import math
from typing import List, Dict, Any


def load_parts_data(json_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Parts data file not found: {json_path}")
    with open(json_path, 'r') as f:
        return json.load(f)


def classify_parts_by_keywords(parts_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group parts by likely roles based on their names.
    """
    categories = {"core": [], "wing": [], "engine": [], "detail": []}
    for part in parts_data:
        name = part.get("name", "").lower()

        if "hull" in name or "bridge" in name or "core" in name:
            categories["core"].append(part)
        elif "wing" in name or "sail" in name:
            categories["wing"].append(part)
        elif "engine" in name or "thruster" in name:
            categories["engine"].append(part)
        elif "antenna" in name or "dish" in name or "greeble" in name or "panel" in name or "cap" in name or "connector" in name or "handle" in name:
            categories["detail"].append(part)
        else:
            # Fallback: assign by size type
            size_type = part.get("size_type", "")
            if size_type == "Big":
                categories["core"].append(part)
            elif size_type == "Medium":
                categories["wing"].append(part)
            else:
                categories["detail"].append(part)

    return categories


def generate_spaceship_layout(parts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    categorized = classify_parts_by_keywords(parts_data)
    layout = []

    # Core
    if categorized["core"]:
        core = random.choice(categorized["core"])
        layout.append({"name": core["name"], "position": [0, 0, 0], "size_type": core.get("size_type", "Big"), "role": "core"})
    else:
        print("[Warning] No core parts found. Falling back to a random part.")
        fallback = random.choice(parts_data)
        layout.append({"name": fallback["name"], "position": [0, 0, 0], "size_type": fallback.get("size_type", "Big"), "role": "core"})

    # Wings
    for side in [-1, 1]:
        if categorized["wing"]:
            wing = random.choice(categorized["wing"])
            position = [side * 5, 0, 0]
            layout.append({"name": wing["name"], "position": position, "size_type": wing.get("size_type", "Medium"), "role": "wing"})

    # Engines
    num_engines = min(len(categorized["engine"]), random.randint(1, 2))
    for i in range(num_engines):
        engine = random.choice(categorized["engine"])
        position = [0, 0, -5 - i * 3]
        layout.append({"name": engine["name"], "position": position, "size_type": engine.get("size_type", "Medium"), "role": "engine"})

    # Details
    num_details = min(len(categorized["detail"]), random.randint(2, 4))
    for i in range(num_details):
        detail = random.choice(categorized["detail"])
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(2, 4)
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        y = random.uniform(-1, 1)
        layout.append({"name": detail["name"], "position": [x, y, z], "size_type": detail.get("size_type", "Small"), "role": "detail"})

    return layout


def save_layout_to_json(layout: List[Dict[str, Any]], output_path: str) -> None:
    with open(output_path, 'w') as f:
        json.dump(layout, f, indent=2)
    print(f"[OK] Spaceship layout saved to: {output_path}")


def main():
    input_path = os.environ.get("HIP", "") + "/batch_import_analysis.json"
    output_path = os.environ.get("HIP", "") + "/spaceship_layout.json"

    parts_data = load_parts_data(input_path)
    layout = generate_spaceship_layout(parts_data)

    if layout:
        save_layout_to_json(layout, output_path)
        print("[Summary]")
        print(f"Core parts: {sum(1 for p in layout if p['role'] == 'core')}")
        print(f"Wings: {sum(1 for p in layout if p['role'] == 'wing')}")
        print(f"Engines: {sum(1 for p in layout if p['role'] == 'engine')}")
        print(f"Details: {sum(1 for p in layout if p['role'] == 'detail')}")
    else:
        print("[Error] Failed to generate layout")


if __name__ == "__main__":
    main()
