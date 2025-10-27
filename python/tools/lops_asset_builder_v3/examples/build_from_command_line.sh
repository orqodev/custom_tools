#!/bin/bash

# Example shell script for building assets from command line using hython
# Usage: ./build_from_command_line.sh /path/to/config.json

# Set up environment
export JOB="/path/to/your/project"
export HOUDINI_USER_PREF_DIR="$HOME/houdini21.0"

# Path to config file (first argument)
CONFIG_FILE="$1"

if [ -z "$CONFIG_FILE" ]; then
    echo "Usage: $0 <config.json>"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    exit 1
fi

# Create temporary Python script
TEMP_SCRIPT=$(mktemp /tmp/houdini_build_XXXXXX.py)

cat > "$TEMP_SCRIPT" << 'PYTHON_SCRIPT'
import sys
import os

# Get config file from command line
config_file = sys.argv[1]

print(f"Building asset from config: {config_file}")
print("="*60)

# Import the CLI
from tools.lops_asset_builder_v3 import lops_asset_builder_cli

# Build the asset
result = lops_asset_builder_cli.build_asset_from_file(config_file, verbose=True)

# Report result
print("="*60)
if result.success:
    print(f"✓ SUCCESS: {result.message}")
    print(f"  Duration: {result.duration:.2f}s")
    if result.output_node:
        print(f"  Output: {result.output_node.path()}")
    sys.exit(0)
else:
    print(f"✗ FAILED: {result.message}")
    if result.error:
        print(f"  Error: {result.error}")
    sys.exit(1)
PYTHON_SCRIPT

# Run with hython
echo "Starting Houdini build process..."
hython "$TEMP_SCRIPT" "$CONFIG_FILE"

# Capture exit code
EXIT_CODE=$?

# Cleanup
rm -f "$TEMP_SCRIPT"

# Exit with same code as hython
exit $EXIT_CODE
