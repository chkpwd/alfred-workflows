#!/usr/bin/env bash
set -e

VENDOR_DIR="vendor"

# Remove existing vendor directory if it exists
if [ -d "$VENDOR_DIR" ]; then
    echo "Removing existing $VENDOR_DIR directory..."
    rm -rf "$VENDOR_DIR"
fi

mkdir -p "$VENDOR_DIR"

# Install dependencies into the vendor directory
echo "Installing dependencies into $VENDOR_DIR..."
pip install --ignore-installed --target="$VENDOR_DIR" -r requirements.txt

echo "Dependencies installed successfully."
