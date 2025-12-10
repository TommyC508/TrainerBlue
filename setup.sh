#!/bin/bash
# Quick start script for Pokemon Showdown Agent

echo "=== Pokemon Showdown Agent Setup ==="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Create directories
mkdir -p logs models data replays
echo "✓ Directories created"

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠ No .env file found. Creating from example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "Please edit .env and add your Pokemon Showdown credentials:"
    echo "  PS_USERNAME=your_username"
    echo "  PS_PASSWORD=your_password (optional for guest)"
    echo ""
else
    echo "✓ .env file exists"
fi

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To run the agent:"
echo "  source venv/bin/activate"
echo "  python -m src.main --agent heuristic --battles 1"
echo ""
echo "For more options:"
echo "  python -m src.main --help"
echo ""
