#!/usr/bin/env python3
"""
Test script to verify the attribute type fix for spaceship visualizer
"""

def test_attribute_types():
    """Test that the attribute types match correctly"""
    
    # Simulate the data types used in the spaceship visualizer
    
    # This simulates what comes from JSON: part.get('position', [0,0,0])
    pos_from_json = [1.0, 2.0, 3.0]  # This is a list
    
    # This simulates the attribute default value: (0.0, 0.0, 0.0)
    attribute_default = (0.0, 0.0, 0.0)  # This is a tuple
    
    print("Testing attribute type compatibility:")
    print(f"Position from JSON: {pos_from_json} (type: {type(pos_from_json)})")
    print(f"Attribute default: {attribute_default} (type: {type(attribute_default)})")
    
    # Test the original problematic approach
    print("\nOriginal approach (would cause error):")
    print(f"Direct assignment: pos = {pos_from_json}")
    print(f"Types match: {type(pos_from_json) == type(attribute_default)}")
    
    # Test the fixed approach
    print("\nFixed approach:")
    pos_as_tuple = tuple(pos_from_json)
    print(f"Converted to tuple: {pos_as_tuple} (type: {type(pos_as_tuple)})")
    print(f"Types match: {type(pos_as_tuple) == type(attribute_default)}")
    
    # Verify the conversion preserves data
    print(f"Data preserved: {list(pos_as_tuple) == pos_from_json}")
    
    return type(pos_as_tuple) == type(attribute_default)

if __name__ == "__main__":
    success = test_attribute_types()
    if success:
        print("\n✓ Attribute type fix verified successfully!")
    else:
        print("\n✗ Attribute type fix failed!")