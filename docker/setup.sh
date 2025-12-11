#!/bin/bash
# DISCOVER Docker Setup Script
# Creates required directories and .env file

set -e

echo "Setting up DISCOVER Docker environment..."

# Navigate to project root (parent of docker directory)
cd "$(dirname "$0")/.."

# Create required directories
echo "Creating directories..."
mkdir -p cache cml data log

echo "Directories created:"
ls -ld cache cml data log

# Check if .env exists in docker directory
if [ ! -f docker/.env ]; then
    echo ""
    echo "Creating docker/.env file from template..."
    cp docker/.env.docker.example docker/.env

    # Set UID and GID
    echo "" >> docker/.env
    echo "# Auto-generated user/group IDs" >> docker/.env
    echo "UID=$(id -u)" >> docker/.env
    echo "GID=$(id -g)" >> docker/.env

    echo "Created docker/.env with your user credentials"
    echo "UID=$(id -u), GID=$(id -g)"
else
    echo ""
    echo "docker/.env already exists, skipping..."
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone discover-modules to cml/:"
echo "   git clone https://github.com/hcmlab/discover-modules.git cml"
echo ""
echo "2. Edit docker/.env to customize settings (optional)"
echo ""
echo "3. Start DISCOVER:"
echo "   cd docker && docker compose up -d"
