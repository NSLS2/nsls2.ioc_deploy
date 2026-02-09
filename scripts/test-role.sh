#!/bin/bash

# EPICS container deployment script
set -e

# Change to script directory
cd "$(dirname "$0")/.."

# Parse arguments
ROLE="$1"

# Validate arguments
if [ -z "$ROLE" ]; then
    echo "Error: Role name required"
    echo "Usage: $0 <role>"
    exit 1
fi

ROLE_DIR="roles/device_roles/$ROLE"
EXAMPLES_DIR="$ROLE_DIR/examples"

# Collect all examples to test
declare -a EXAMPLES=()
declare -a CONFIG_FILES=()

if [ -d "$EXAMPLES_DIR" ]; then
    # New structure: examples/<name>/config.yml
    for example_dir in "$EXAMPLES_DIR"/*/; do
        if [ -d "$example_dir" ]; then
            example_name=$(basename "$example_dir")
            config_file="$example_dir/config.yml"
            if [ -f "$config_file" ]; then
                EXAMPLES+=("$example_name")
                CONFIG_FILES+=("$config_file")
            fi
        fi
    done
fi

# Also check for legacy example.yml
if [ -f "$ROLE_DIR/example.yml" ]; then
    EXAMPLES+=("legacy")
    CONFIG_FILES+=("$ROLE_DIR/example.yml")
fi

if [ ${#EXAMPLES[@]} -eq 0 ]; then
    echo "Error: No example configurations found for role '$ROLE'"
    exit 1
fi

echo "Found ${#EXAMPLES[@]} example(s) to test: ${EXAMPLES[*]}"

# Install collection (idempotent)
echo "Installing ansible collection..."
ansible-galaxy collection install -r collections/requirements.yml
ansible-galaxy collection install $(pwd) --force
ansible-galaxy collection install community.docker

# Verify container is running
if [ -z "$(docker ps -q -f name=epics-dev)" ]; then
    echo "Error: Container 'epics-dev' is not running."
    exit 1
fi

# Install required packages
# Note: root access required for package installation and system file modification
echo "Installing required packages..."
docker exec -u root epics-dev yum install -y python3-dnf wget > /dev/null 2>&1
docker exec -u root epics-dev yum install -y epel-release > /dev/null 2>&1
docker exec -u root epics-dev yum install -y seq > /dev/null 2>&1 || true

# Install Pixi (pinned version with checksum validation)
PIXI_VERSION="v0.55.0"
PIXI_SHA256="cb733205ae1a02986071bcbeff47c60460bfb92d1cd9565d40f4dea5448c86a5"
echo "Installing Pixi ${PIXI_VERSION}..."
docker exec -u root epics-dev bash -c "
    curl -fsSL -o /tmp/pixi.tar.gz https://github.com/prefix-dev/pixi/releases/download/$PIXI_VERSION/pixi-x86_64-unknown-linux-musl.tar.gz
    echo '$PIXI_SHA256  /tmp/pixi.tar.gz' | sha256sum -c -
    tar -xzf /tmp/pixi.tar.gz -C /tmp
    chmod +x /tmp/pixi
    mv /tmp/pixi /usr/local/bin/pixi
    rm /tmp/pixi.tar.gz
"

echo "Setting up Python environment with Pixi..."
docker exec -u root epics-dev bash -c '
    if [ ! -f pixi.toml ]; then
        pixi init
    fi
    pixi add python=3.12 pyyaml
'

# Test each example
declare -a FAILED_EXAMPLES=()
for i in "${!EXAMPLES[@]}"; do
    EXAMPLE="${EXAMPLES[$i]}"
    CONFIG_FILE="${CONFIG_FILES[$i]}"

    echo ""
    echo "========================================"
    echo "Testing example: $EXAMPLE"
    echo "========================================"

    # Get the first IOC name from config file
    IOC_NAME=$(grep -E "^\s*[a-zA-Z0-9_-]+:" "$CONFIG_FILE" | head -1 | sed 's/^[[:space:]]*//' | sed 's/://')

    # Create merged config with host_config wrapping the IOC config
    TEMP_CONFIG=$(mktemp)

    cat > "$TEMP_CONFIG" << EOF
host_config:
  softioc_user: softioc-tst
  softioc_group: softioc-tst
  epics_interface:
    address: 127.0.0.1
    broadcast: 127.255.255.255
EOF

    # Append IOC config from config file indented under host_config (skip --- line)
    grep -v "^---" "$CONFIG_FILE" | sed 's/^/  /' >> "$TEMP_CONFIG"

    echo "Deploying IOC: $IOC_NAME"

    # Clean up any existing deployment for this IOC
    docker exec -u root epics-dev rm -rf "/epics/iocs/$IOC_NAME"

    # Check if verify.yml specifies skip_compilation
    SKIP_COMPILATION="false"
    VERIFY_FILE="$EXAMPLES_DIR/$EXAMPLE/verify.yml"
    if [ "$EXAMPLE" != "legacy" ] && [ -f "$VERIFY_FILE" ]; then
        if grep -q "skip_compilation: true" "$VERIFY_FILE"; then
            SKIP_COMPILATION="true"
            echo "Skipping module compilation (skip_compilation: true in verify.yml)"
        fi
    fi

    if ! ansible-playbook --diff -i epics-dev, -c docker -u root \
        -e "deploy_ioc_ioc_name=$IOC_NAME" \
        -e "deploy_ioc_target=$IOC_NAME" \
        -e "install_module_default_pkg_deps=[]" \
        -e "install_module_skip_compilation=$SKIP_COMPILATION" \
        -e "@$TEMP_CONFIG" \
        --start-at-task "Deploy specified IOCs" \
        scripts/deploy_ioc.yml; then
        echo "FAILED: Deployment failed for example: $EXAMPLE"
        FAILED_EXAMPLES+=("$EXAMPLE (deployment)")
        rm -f "$TEMP_CONFIG"
        continue
    fi

    rm -f "$TEMP_CONFIG"

    # Run verification if verify.yml exists (only for new-style examples)
    if [ "$EXAMPLE" != "legacy" ] && [ -f "$VERIFY_FILE" ]; then
        echo ""
        echo "Running deployment verification..."

        # Copy verification script and verify.yml to container, then run inside
        docker cp scripts/verify_deployment.py epics-dev:/tmp/
        docker cp "$VERIFY_FILE" epics-dev:/tmp/verify.yml

        # Run verification inside the container using Pixi Python
        if ! docker exec -u root epics-dev pixi run python /tmp/verify_deployment.py \
            /tmp/verify.yml "/epics/iocs/$IOC_NAME"; then
            echo "FAILED: Verification failed for example: $EXAMPLE"
            FAILED_EXAMPLES+=("$EXAMPLE (verification)")
        fi
    else
        echo "Skipping verification (no verify.yml found)"
    fi
done

echo ""
echo "========================================"
if [ ${#FAILED_EXAMPLES[@]} -eq 0 ]; then
    echo "PASSED: All ${#EXAMPLES[@]} example(s) passed"
    exit 0
else
    echo "FAILED: ${#FAILED_EXAMPLES[@]} of ${#EXAMPLES[@]} example(s) failed:"
    for failed in "${FAILED_EXAMPLES[@]}"; do
        echo "  - $failed"
    done
    exit 1
fi
