#!/bin/bash

# Navigate to the ztv-local-app directory in Documents
cd "$HOME/Documents/Zinnia/ztv-local-app" || {
    echo "Error: ztv-local-app directory not found in Documents."
    exit 1
}

# Start the Daily Chronicle program
python3 -m daily_chronicle.main || {
    echo "Error: Failed to start the Daily Chronicle program."
    exit 1
}

echo "✅ Daily Chronicle started successfully."
