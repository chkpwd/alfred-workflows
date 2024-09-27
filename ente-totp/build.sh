#!/bin/bash

# Build script for packaging an Alfred workflow without external dependencies

# Exit immediately if a command exits with a non-zero status
set -e

# Call build_deps.sh first
echo "Running build_deps.sh..."
./build_deps.sh

# Extract the workflow name from info.plist using the Python script
WORKFLOW_NAME=$(python3 build_tools.py --get-name)

# Check if WORKFLOW_VERSION environment variable is set, otherwise use default
VERSION=${WORKFLOW_VERSION:-"1.0.0"}

# Output filename
OUTPUT_FILE="${WORKFLOW_NAME}-${VERSION}.alfredworkflow"

# Clean up any previous builds
clean() {
	rm -f "$OUTPUT_FILE"
}

# Function to package the directory
zip_dir() {
    find . \
        -path "./.*" -prune -o \
        -type f \
        -not -name "*.md" \
        -not -name "*.log" \
        -not -name "*.alfredworkflow" \
        -not -name "requirements.*" \
        -not -name "*.pyc" \
        -not -path "*/__pycache__/*" \
        -not -path "./build*" \
        -print | zip --symlinks -@ "$OUTPUT_FILE"
}

# Main execution
clean
echo "Updating version in info.plist..."
python3 build_tools.py --set-version "${VERSION}"
echo "Packaging the workflow..."
zip_dir
# if in github action, write build file path to GITHUB_OUTPUT
[[ -n "$GITHUB_OUTPUT" ]] && echo "OUTPUT_FILE=${PWD}/${OUTPUT_FILE}" >> "$GITHUB_OUTPUT"
echo "Packaged $OUTPUT_FILE successfully!"
