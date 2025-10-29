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
    exit 1
fi

# Install collection (idempotent)
echo "Installing ansible collection..."
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

# Create missing RULES_SNCSEQ file
echo "Creating missing EPICS SNCSEQ rules..."
docker exec -u root epics-dev bash -c 'cat > /usr/lib/epics/configure/rules.d/RULES_SNCSEQ << EOF
# SNCSEQ Rules - minimal implementation for compatibility
# This file provides basic SNCSEQ support for EPICS builds

ifndef SNCSEQ_RULES
SNCSEQ_RULES = YES

# Define empty rules to prevent build failures
SNCSEQ_RULES_INCLUDED = YES

endif
EOF'

# Get example.yml for the role
EXAMPLE_FILE="../nsls2.ioc_deploy/roles/device_roles/$ROLE/example.yml"

# Validate example.yml exists
if [ ! -f "$EXAMPLE_FILE" ]; then
    echo "Error: No example.yml found for role '$ROLE'"
    exit 1
fi

# Get the first IOC name from example.yml
IOC_NAME=$(grep -E "^\s*[a-zA-Z0-9_-]+:" "$EXAMPLE_FILE" | head -1 | sed 's/^[[:space:]]*//' | sed 's/://')

# Create merged config with host_config wrapping the IOC config
TEMP_CONFIG=$(mktemp)
trap "rm -f $TEMP_CONFIG" EXIT

cat > "$TEMP_CONFIG" << EOF
host_config:
  softioc_user: softioc-tst
  softioc_group: softioc-tst
  epics_interface:
    address: 127.0.0.1
    broadcast: 127.255.255.255
EOF

# Append IOC config from example.yml indented under host_config (skip --- line)
grep -v "^---" "$EXAMPLE_FILE" | sed 's/^/  /' >> "$TEMP_CONFIG"

# Test deployment
echo "Testing role: $ROLE with IOC: $IOC_NAME"

ansible-playbook -i epics-dev, -c docker -u root \
  -e "deploy_ioc_ioc_name=$IOC_NAME" \
  -e "deploy_ioc_target=$IOC_NAME" \
  -e "install_module_default_pkg_deps=[]" \
  -e "@$TEMP_CONFIG" \
  --start-at-task "Deploy specified IOCs" \
  scripts/deploy_ioc.yml
