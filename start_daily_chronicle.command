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

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv .venv || {
        echo "❌ Error: Failed to create virtual environment."
        exit 1
    }
fi

# Activate the virtual environment
source .venv/bin/activate || {
    echo "❌ Error: Failed to activate virtual environment."
    exit 1
}

echo "📦 Installing dependencies..."
pip install -r requirements-trial.txt || { # swap this to requirements.txt later once overwritten
    echo "❌ Error: Failed to install dependencies."
    exit 1
    }

# Start the Daily Chronicle program
python3 -m daily_chronicle.main || {
    echo "❌ Error: Failed to start the Daily Chronicle program."
    exit 1
}

echo "✅ Daily Chronicle started successfully."
