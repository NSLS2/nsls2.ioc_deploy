#!/bin/bash

# EPICS container deployment script
set -e

# Change to script directory
cd "$(dirname "$0")/.."

# Default values
CONTAINER="ghcr.io/nsls2/epics-alma8:latest"
ROLE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --container) CONTAINER="$2"; shift 2 ;;
        *) ROLE="$1"; shift ;;
    esac
done


# Check required repositories exist
echo "Checking required repositories..."
if [[ ! -d "../ansible" ]]; then
    echo "Missing ../ansible - run: git clone https://github.com/nsls2/ansible"
    exit 1
fi
if [[ ! -d "../ioc_host_vars" ]]; then
    echo "Missing ../ioc_host_vars - run: git clone https://github.com/nsls2/ioc_host_vars"
    exit 1
fi

# Install collection (idempotent)
echo "Installing ansible collection..."
ansible-galaxy collection install $(pwd) -p ../ansible/collections --force
ansible-galaxy collection install community.docker

# Verify container is running
if [ -z "$(docker ps -q -f name=epics-dev)" ]; then
    echo "Error: Container 'epics-dev' is not running."
    exit 1
fi

# Install required packages
echo "Installing required packages..."
docker exec -u root epics-dev yum install -y python3-dnf
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

# Get the first IOC name from example.yml
IOC_NAME=$(grep -E "^[a-zA-Z0-9_-]+:" "$EXAMPLE_FILE" | head -1 | sed 's/://')

# Test deployment
echo "Testing role: $ROLE with IOC: $IOC_NAME"
cd ../ansible

ansible-playbook -i epics-dev, -c docker -u root \
  -e "deploy_ioc_ioc_name=$IOC_NAME" \
  -e "deploy_ioc_target=$IOC_NAME" \
  -e '{"host_config":{"softioc_user":"softioc-tst","softioc_group":"softioc-tst","epics_interface":{"address":"127.0.0.1","broadcast":"127.255.255.255"}}}' \
  -e "@$EXAMPLE_FILE" \
  --start-at-task "Deploy specified IOCs" \
  deploy_ioc.yml
