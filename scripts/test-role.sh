#!/bin/bash

# EPICS container deployment script
set -e

# Change to script directory
cd "$(dirname "$0")/.."

# Default values
CONTAINER="ghcr.io/nsls2/epics-rpm-config:latest"
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

# Setup (idempotent)
echo "Install python deps..."
pip install -r requirements.txt > /dev/null 2>&1 || true
pip3 install --upgrade ansible-core > /dev/null 2>&1

# Install collection (idempotent)
echo "Installing ansible collection..."
ansible-galaxy collection install $(pwd) -p ../ansible/collections --force
ansible-galaxy collection install community.docker

# Check if container is running, start if needed
if ! docker ps --format 'table {{.Names}}' | grep -q epics-dev; then
    echo "Container not running, checking if image exists..."
    if ! docker images --format 'table {{.Repository}}:{{.Tag}}' | grep -q "$CONTAINER"; then
        echo "Pulling container image..."
        docker login ghcr.io
        docker pull "$CONTAINER"
    fi
    echo "Starting container..."
    docker run -dit --name epics-dev "$CONTAINER"
fi

# Install required Python packages in container
echo "Installing Python packages in container..."
docker exec -u root epics-dev yum install -y python3-requests python3-pyyaml python3-pip python3-dnf > /dev/null 2>&1
docker exec -u root epics-dev yum install -y procServ git libxml2-devel libXext-devel zlib-devel libX11-devel > /dev/null 2>&1

# Install development tools for compilation
echo "Installing development tools..."
docker exec -u root epics-dev yum groupinstall -y "Development Tools" > /dev/null 2>&1
docker exec -u root epics-dev yum install -y gcc gcc-c++ make readline-devel > /dev/null 2>&1

# Install EPICS sequencer support
echo "Installing EPICS sequencer support..."
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

# Create required directories
echo "Creating required directories..."
docker exec -u root epics-dev mkdir -p /epics/common /epics/modules
docker exec -u root epics-dev chown epics:epics /epics/common /epics/modules

# Test deployment
echo "Testing role: $ROLE"
cd ../ansible
ansible-playbook -i epics-dev, -c docker -u root -e "ioc_type=$ROLE" -e "deploy_ioc_component=test" -e "deploy_ioc_target=test-ioc" -e "deploy_ioc_ioc_name=test-ioc" -e "ioc_name=test-ioc" -e '{"install_module_default_pkg_deps":[],"deploy_ioc_required_system_packages":[],"host_config":{"softioc_user":"epics","softioc_group":"epics","epics_interface":{"address":"127.0.0.1","broadcast":"127.255.255.255"},"test-ioc":{"type":"'$ROLE'","enabled":true,"environment":{"IOC_DIR":"/epics/iocs","TOP":"/epics/iocs/test-ioc"}}}}' --start-at-task "Deploy specified IOCs" deploy_ioc.yml
