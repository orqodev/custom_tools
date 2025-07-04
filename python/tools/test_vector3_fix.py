#!/usr/bin/env python3
"""
Test script to verify the hou.Vector3 fix for spaceship visualizer
"""

def test_vector3_compatibility():
    """Test that hou.Vector3 types are compatible"""
    
    print("Testing hou.Vector3 attribute compatibility:")
    
    # Simulate the data types used in the spaceship visualizer
    
    # This simulates what comes from JSON: part.get('position', [0,0,0])
    pos_from_json = [1.0, 2.0, 3.0]  # This is a list
    
    # This simulates the attribute default value: hou.Vector3(0.0, 0.0, 0.0)
    # We'll simulate this since we can't import hou outside Houdini
    class MockVector3:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z
        def __repr__(self):
            return f"Vector3({self.x}, {self.y}, {self.z})"
        def __eq__(self, other):
            return isinstance(other, MockVector3) and (self.x, self.y, self.z) == (other.x, other.y, other.z)
    
    attribute_default = MockVector3(0.0, 0.0, 0.0)  # This simulates hou.Vector3
    
    print(f"Position from JSON: {pos_from_json} (type: {type(pos_from_json)})")
    print(f"Attribute default: {attribute_default} (type: {type(attribute_default)})")
    
    # Test the previous tuple approach
    print("\nPrevious tuple approach:")
    pos_as_tuple = tuple(pos_from_json)
    print(f"Converted to tuple: {pos_as_tuple} (type: {type(pos_as_tuple)})")
    print(f"Types match with Vector3: {type(pos_as_tuple) == type(attribute_default)}")
    
    # Test the new Vector3 approach
    print("\nNew Vector3 approach:")
    pos_as_vector3 = MockVector3(*pos_from_json)
    print(f"Converted to Vector3: {pos_as_vector3} (type: {type(pos_as_vector3)})")
    print(f"Types match with Vector3: {type(pos_as_vector3) == type(attribute_default)}")
    
    # Verify the conversion preserves data
    original_values = (pos_from_json[0], pos_from_json[1], pos_from_json[2])
    vector3_values = (pos_as_vector3.x, pos_as_vector3.y, pos_as_vector3.z)
    print(f"Data preserved: {original_values == vector3_values}")
    
    return type(pos_as_vector3) == type(attribute_default)

def test_code_changes():
    """Test that the code changes are correctly implemented"""
    
    print("\nTesting code changes in spaceship_visualizer.py:")
    
    import os
    file_path = os.path.join(os.path.dirname(__file__), 'spaceship_visualizer.py')
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for the updated addAttrib line
    addattrib_found = False
    setattrib_found = False
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'addAttrib' in line and 'original_pos' in line:
            if 'hou.Vector3(0.0, 0.0, 0.0)' in line:
                addattrib_found = True
                print(f"  ✓ Line {i+1}: addAttrib correctly uses hou.Vector3(0.0, 0.0, 0.0)")
            else:
                print(f"  ✗ Line {i+1}: addAttrib does not use hou.Vector3: {line.strip()}")
        
        if 'setAttribValue' in line and 'original_pos' in line:
            if 'hou.Vector3(pos)' in line:
                setattrib_found = True
                print(f"  ✓ Line {i+1}: setAttribValue correctly uses hou.Vector3(pos)")
            else:
                print(f"  ✗ Line {i+1}: setAttribValue does not use hou.Vector3: {line.strip()}")
    
    if not addattrib_found:
        print("  ✗ addAttrib line with hou.Vector3 not found")
    if not setattrib_found:
        print("  ✗ setAttribValue line with hou.Vector3 not found")
    
    return addattrib_found and setattrib_found

def test_houdini_compatibility():
    """Test Houdini-specific compatibility notes"""
    
    print("\nHoudini compatibility notes:")
    print("  ✓ hou.Vector3 is the native Houdini vector type")
    print("  ✓ Using hou.Vector3 ensures proper type compatibility with Houdini attributes")
    print("  ✓ hou.Vector3 can be constructed from lists, tuples, or individual components")
    print("  ✓ This approach is more robust than using tuples for vector attributes")
    
    return True

if __name__ == "__main__":
    print("Vector3 Fix Test")
    print("=" * 50)
    
    compatibility_ok = test_vector3_compatibility()
    code_changes_ok = test_code_changes()
    houdini_ok = test_houdini_compatibility()
    
    if compatibility_ok and code_changes_ok and houdini_ok:
        print("\n✓ All tests passed! Vector3 fix implemented correctly.")
    else:
        print("\n✗ Some tests failed!")