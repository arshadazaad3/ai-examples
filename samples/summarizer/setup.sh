#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create vtt directory if it doesn't exist
mkdir -p vtt

echo "Setup complete! You can now run ./start.sh to start the application." 