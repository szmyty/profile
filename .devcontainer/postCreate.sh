#!/bin/bash
# Post-create script for devcontainer setup

set -e

echo "🚀 Setting up development environment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get install -y jq curl shellcheck

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Install svgo for SVG optimization
echo "🎨 Installing SVG optimization tools..."
sudo npm install -g svgo

# Create mock data directory
echo "📁 Creating mock data directory..."
mkdir -p data/mock

echo "✅ Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  - Run tests: python -m pytest tests/ -v"
echo "  - Run pre-commit: pre-commit run --all-files"
echo "  - Generate cards: See scripts/ directory"
echo ""
echo "Happy coding! 🎉"
