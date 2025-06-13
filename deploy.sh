#!/bin/bash

echo "🚀 DISASTER WASTE TRACKER - SIMPLIFIED DEPLOYMENT"
echo "================================================"

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "Installing SAM CLI..."
    pip3 install aws-sam-cli
fi

echo "✅ Ready for deployment!"
echo "Next steps:"
echo "1. Run: sam init"
echo "2. Choose: AWS Quick Start Templates"
echo "3. Choose: Hello World Example"
echo "4. Runtime: python3.9"
echo "5. Name: disaster-waste-tracker"

