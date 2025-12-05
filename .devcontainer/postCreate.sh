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

# Install act for running GitHub Actions locally
echo "🎭 Installing act (GitHub Actions runner)..."
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Create mock data directory
echo "📁 Creating mock data directory..."
mkdir -p data/mock

# Create act configuration
echo "⚙️ Setting up act configuration..."
cat > .actrc << 'EOF'
# act configuration file
# Use the medium-sized Ubuntu image for better compatibility
-P ubuntu-latest=catthehacker/ubuntu:act-latest
-P ubuntu-22.04=catthehacker/ubuntu:act-22.04
-P ubuntu-20.04=catthehacker/ubuntu:act-20.04

# Enable verbose output for debugging
--verbose

# Use GitHub token from environment if available
--env GITHUB_TOKEN
EOF

# Create secrets template for local testing
echo "🔐 Creating secrets template..."
cat > .secrets.example << 'EOF'
# Local secrets for act - Copy this file to .secrets and fill in your values
# DO NOT commit .secrets to version control - it's already in .gitignore

# GitHub token for API access (optional - can use GITHUB_TOKEN from environment)
GITHUB_TOKEN=your_github_token_here

# Optional API tokens for data fetching
MAPBOX_TOKEN=your_mapbox_token_here
OURA_PAT=your_oura_token_here

# Repository information (usually auto-detected by act)
GITHUB_REPOSITORY=szmyty/profile
GITHUB_REPOSITORY_OWNER=szmyty
EOF

# Ensure .secrets is in .gitignore
if ! grep -q "^\.secrets$" .gitignore 2>/dev/null; then
    echo ".secrets" >> .gitignore
fi

echo "✅ Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  - Run tests: python -m pytest tests/ -v"
echo "  - Run pre-commit: pre-commit run --all-files"
echo "  - Generate cards: See scripts/ directory"
echo "  - Run GitHub Actions locally: act -j <job-name>"
echo ""
echo "📝 GitHub Actions (act) setup:"
echo "  1. Copy .secrets.example to .secrets and add your tokens"
echo "  2. Run 'act -l' to list available workflows"
echo "  3. Run 'act -j <job-name>' to run a specific job"
echo "  4. Example: 'act -j test-python' to run Python tests"
echo ""
echo "Happy coding! 🎉"
