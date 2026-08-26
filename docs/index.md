# nsls2.ioc_deploy

Ansible collection for centralized EPICS IOC deployment at NSLS-II.

## Overview

The `nsls2.ioc_deploy` collection provides a standardized framework for deploying EPICS IOC instances across NSLS-II beamline infrastructure. It automates:

- Building EPICS modules from source with automatic dependency resolution
- Generating IOC startup scripts, environment files, and autosave configurations
- Deploying hardware-specific IOC configurations via reusable device roles
- Managing IOC services through systemd and procServ

## Architecture

The collection is designed around three core roles:

| Role | Purpose |
|------|---------|
| `deploy_ioc` | Central deployment logic shared by all IOC types |
| `install_module` | Builds EPICS modules from source with dependency resolution |
| `manage_iocs` | Manages IOC services (start/stop/restart via systemd) |

Each supported hardware type has a **device role** under `roles/device_roles/` that customizes the deployment for that specific IOC type.

## Quick Start

```bash
# Install pixi (if not already installed)
curl -fsSL https://pixi.sh/install.sh | bash

# Create a new device role
pixi run make-role

# Test locally against a container
pixi run deployment -t <role-name> --container -m 8
```

## Repository Structure

```
roles/
├── deploy_ioc/          # Core deployment role
│   ├── defaults/        # Default variable values
│   ├── tasks/           # Ansible tasks
│   ├── templates/       # Jinja2 templates for IOC files
│   └── vars/            # Per-IOC-type variable overrides
├── device_roles/        # One directory per hardware type
│   ├── adaravis/
│   ├── adsimdetector/
│   ├── tetramm/
│   └── ...
├── install_module/      # Module compilation role
│   ├── defaults/        # Default compilation settings
│   ├── tasks/           # Build tasks
│   └── vars/            # Per-module build configurations
└── manage_iocs/         # Service management role
```

## Key Commands

| Command | Purpose |
|---------|---------|
| `pixi run make-role` | Create a new device role interactively |
| `pixi run make-module` | Create a new installable module |
| `pixi run update-module` | Update an existing module version |
| `pixi run delete-role` | Remove a device role |
| `pixi run delete-module` | Remove a module |
| `pixi run report` | View all supported modules and roles |
| `pixi run tests` | Run the test suite |
| `pixi run deployment -t <type>` | Deploy a role locally |
| `pixi run lint` | Run linting checks |
