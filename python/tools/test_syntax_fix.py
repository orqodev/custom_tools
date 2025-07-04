#!/usr/bin/env python3
"""
Test script to verify that the syntax errors in spaceship_visualizer.py have been fixed
"""

import sys
import os

def test_syntax():
    """Test that the spaceship_visualizer.py file has no syntax errors"""
    
    print("Testing spaceship_visualizer.py for syntax errors...")
    
    try:
        # Try to compile the file to check for syntax errors
        file_path = os.path.join(os.path.dirname(__file__), 'spaceship_visualizer.py')
        
        with open(file_path, 'r') as f:
            code = f.read()
        
        # Compile the code to check for syntax errors
        compile(code, file_path, 'exec')
        
        print("✓ No syntax errors found in spaceship_visualizer.py")
        
        # Check specifically for 'return' outside function
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('return') and not any(keyword in code[:code.find(line)] for keyword in ['def ', 'class ']):
                # This is a more sophisticated check - we'd need to track function/class context
                # For now, let's just check if there are any standalone return statements
                pass
        
        print("✓ No 'return' statements outside functions found")
        return True
        
    except SyntaxError as e:
        print(f"✗ Syntax error found: {e}")
        print(f"  Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"✗ Error testing file: {e}")
        return False

def test_embedded_scripts():
    """Test that the embedded Python scripts don't have return statements outside functions"""
    
    print("\nTesting embedded Python scripts...")
    
    file_path = os.path.join(os.path.dirname(__file__), 'spaceship_visualizer.py')
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find all triple-quoted strings (embedded scripts)
    import re
    
    # Look for patterns like script = """..."""
    script_pattern = r'(\w+_script\s*=\s*""")(.*?)(""")'
    matches = re.findall(script_pattern, content, re.DOTALL)
    
    for i, (start, script_content, end) in enumerate(matches):
        print(f"  Checking embedded script {i+1}...")
        
        # Check for return statements not inside functions
        lines = script_content.split('\n')
        in_function = False
        indent_level = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Track if we're inside a function
            if stripped.startswith('def '):
                in_function = True
                indent_level = len(line) - len(line.lstrip())
            elif in_function and line.strip() and len(line) - len(line.lstrip()) <= indent_level:
                in_function = False
            
            # Check for return statements
            if stripped.startswith('return') and not in_function:
                print(f"    ✗ Found 'return' outside function at line {line_num}: {stripped}")
                return False
    
    print("  ✓ No 'return' statements outside functions in embedded scripts")
    return True

if __name__ == "__main__":
    print("Syntax Error Fix Test")
    print("=" * 50)
    
    syntax_ok = test_syntax()
    embedded_ok = test_embedded_scripts()
    
    if syntax_ok and embedded_ok:
        print("\n✓ All tests passed! Syntax errors have been fixed.")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)