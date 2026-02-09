#!/bin/bash

CONTAINER_NAME="$1"
RHEL_VERSION="$2"

# Verify required arguments are provided
if [ -z "$CONTAINER_NAME" ] || [ -z "$RHEL_VERSION" ]; then
    echo "Error: Missing required arguments"
    echo "Usage: $0 <container_name> <rhel_version>"
    exit 1
fi

REQUIRED_IMAGE="ghcr.io/nsls2/epics-alma$RHEL_VERSION:latest"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Verifying that container '$CONTAINER_NAME' is running the required image '$REQUIRED_IMAGE'..."

# Verify container is running
if [ -z "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Starting container '$CONTAINER_NAME'..."
    docker run -dit --name $CONTAINER_NAME $REQUIRED_IMAGE
else
    echo "Container '$CONTAINER_NAME' is already running."
fi

# Verify container is running the required image
CURRENT_IMAGE=$(docker inspect -f '{{.Config.Image}}' $CONTAINER_NAME)
if [ "$CURRENT_IMAGE" != "$REQUIRED_IMAGE" ]; then
    echo "Error: Container '$CONTAINER_NAME' is running image '$CURRENT_IMAGE', but '$REQUIRED_IMAGE' is required."
    exit 1
fi

# Install required packages
# Note: root access required for package installation and system file modification
echo "Installing required packages..."
docker exec -u root $CONTAINER_NAME dnf install -y python3-dnf wget > /dev/null 2>&1
docker exec -u root $CONTAINER_NAME dnf install -y epel-release > /dev/null 2>&1
docker exec -u root $CONTAINER_NAME dnf install -y seq > /dev/null 2>&1 || true

# Install Pixi (pinned version with checksum validation)
PIXI_VERSION="v0.55.0"
PIXI_SHA256="cb733205ae1a02986071bcbeff47c60460bfb92d1cd9565d40f4dea5448c86a5"
echo "Installing Pixi ${PIXI_VERSION}..."
docker exec -u root $CONTAINER_NAME bash -c "
    curl -fsSL -o /tmp/pixi.tar.gz https://github.com/prefix-dev/pixi/releases/download/$PIXI_VERSION/pixi-x86_64-unknown-linux-musl.tar.gz
    echo '$PIXI_SHA256  /tmp/pixi.tar.gz' | sha256sum -c -
    tar -xzf /tmp/pixi.tar.gz -C /tmp
    chmod +x /tmp/pixi
    mv /tmp/pixi /usr/local/bin/pixi
    rm /tmp/pixi.tar.gz
"

# Copy over premade Pixi configuration files
echo "Copying Pixi configuration files and verification script..."
docker cp $SCRIPT_DIR/pixi.lock $CONTAINER_NAME:pixi.lock
docker cp $SCRIPT_DIR/pixi.toml $CONTAINER_NAME:pixi.toml
docker cp $SCRIPT_DIR/verify_deployment.py $CONTAINER_NAME:verify_deployment.py

echo "Installing Pixi environment in container..."
docker exec -u root $CONTAINER_NAME pixi install
echo "Container setup complete."