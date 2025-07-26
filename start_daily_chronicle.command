#!/bin/bash

# Navigate to the ztv-local-app directory on the Desktop
cd "$HOME/Desktop/ztv-local-app" || {
    echo "❌ Error: ztv-local-app directory not found on Desktop."
    exit 1
}

# Pull the latest changes from the Git repository
git pull || {
    echo "❌ Error: Failed to pull the latest changes from the git repository."
    exit 1
}

# Activate the virtual environment
source .venv/bin/activate || {
    echo "❌ Error: Failed to activate virtual environment."
    exit 1
}

# Start the Daily Chronicle program
python3 -m daily_chronicle.main || {
    echo "❌ Error: Failed to start the Daily Chronicle program."
    exit 1
}

echo "✅ Daily Chronicle started successfully."
