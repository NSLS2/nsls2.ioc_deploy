# Installation

## Prerequisites

- **pixi** (≥ v0.55.0) — Task runner and environment manager
- **Docker** or **Podman** — For local testing with EPICS containers
- **Git** — For cloning and version management

## Installing pixi

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

## Cloning the Repository

```bash
git clone https://github.com/NSLS2/nsls2.ioc_deploy.git
cd nsls2.ioc_deploy
```

## Installing Dependencies

All Python and Ansible dependencies are managed by pixi. Simply run any pixi task and the environment will be set up automatically:

```bash
pixi run tests
```

Or explicitly install the environment:

```bash
pixi install
```

### Key Dependencies

The pixi environment includes:

| Package | Purpose |
|---------|---------|
| `ansible` | Automation engine for running playbooks |
| `ansible-lint` | Linting for Ansible files |
| `pytest` | Test framework |
| `yamale` | YAML schema validation |
| `questionary` | Interactive prompts for collection management |
| `tabulate` | Report generation |
| `ruff` | Python linting |
| `pre-commit` | Git hook management |

## Setting Up for Local Testing

Local testing deploys IOC roles into Docker/Podman containers running AlmaLinux with EPICS pre-installed.

### Pull the EPICS Container Images

```bash
docker login ghcr.io
docker pull ghcr.io/nsls2/epics-alma8:latest
docker pull ghcr.io/nsls2/epics-alma9:latest
```

### Verify Your Setup

```bash
# Run the test suite (no container needed)
pixi run tests

# Test a specific role against a container
pixi run deployment -t adsimdetector --container -m 8
```

## Installing as an Ansible Collection

If you want to use this collection in your own playbooks:

```bash
ansible-galaxy collection install nsls2.ioc_deploy
```

Or add it to your `requirements.yml`:

```yaml
collections:
  - name: nsls2.ioc_deploy
    source: https://github.com/NSLS2/nsls2.ioc_deploy
    type: git
```

## NSLS-II Network Utilities (Optional)

For deployments to real NSLS-II infrastructure, install the network utility package:

```bash
pixi run install-nsls2network
```

This provides access to beamline network configuration and host lookup utilities.
