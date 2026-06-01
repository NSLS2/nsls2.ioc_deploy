# Local Testing

Local testing allows you to validate your device roles by deploying them into Docker/Podman containers running AlmaLinux with EPICS pre-installed.

## Prerequisites

- **pixi** installed and working
- **Docker** or **Podman** with access to `ghcr.io`
- Logged in to the GitHub Container Registry:
  ```bash
  docker login ghcr.io
  ```

## Quick Start

Test any role against a container:

```bash
pixi run deployment -t <role-name> --container -m <el-version>
```

Examples:

```bash
# Test adsimdetector on EL8
pixi run deployment -t adsimdetector --container -m 8

# Test adsimdetector on EL9
pixi run deployment -t adsimdetector --container -m 9

# Test all roles on both EL8 and EL9
pixi run deploy-all
```

## How It Works

The local testing system:

1. **Starts a container** running `ghcr.io/nsls2/epics-alma{8,9}:latest`
2. **Installs dependencies** in the container (Python, dnf, pixi, EPICS packages)
3. **Runs the Ansible deployment** against the container as if it were a remote host
4. **Verifies the result** using the `verify.yml` schema (if present)

### Container Setup

The `scripts/setup_container.sh` script handles container initialization:

- Installs `python3-dnf`, `wget`, `epel-release`
- Installs a pinned version of pixi with checksum validation
- Copies pixi configuration and the verification script into the container

### Deployment Script

`scripts/deploy_local_config.py` orchestrates the deployment:

```bash
pixi run deployment -t <type> [options]
```

Options:

| Flag | Description |
|------|-------------|
| `-t <type>` | IOC type/role to deploy |
| `--container` | Deploy to a Docker container (vs. localhost) |
| `-m <version>` | EL version (8 or 9) |
| `--all` | Deploy all available roles |
| `--dry-run` | Show what would be deployed without executing |
| `--verbose` | Enable verbose Ansible output |
| `--skip-compilation` | Skip module compilation (for SDK-dependent roles) |

## Example Configurations

Each device role provides example configurations that are used for testing. These can be in two formats:

### Legacy Format (Single Example)

```
roles/device_roles/mydevice/
└── example.yml
```

### New Format (Multiple Examples)

```
roles/device_roles/mydevice/
└── examples/
    └── example-name/
        ├── config.yml       # IOC configuration
        └── verify.yml       # Deployment verification schema
```

The new format supports multiple examples per role and includes verification schemas.

## Running Unit Tests

Unit tests validate configuration files without deploying anything:

```bash
# Run all tests
pixi run tests

# Run specific test files
pixi run tests tests/test_install_module_vars.py
pixi run tests tests/test_deploy_ioc_vars.py
pixi run tests tests/test_device_roles.py
pixi run tests tests/test_validate_ex_configs_against_schemas.py
```

### What the Tests Check

| Test File | What It Validates |
|-----------|-------------------|
| `test_install_module_vars.py` | Module configs match schema, deps exist, naming correct |
| `test_deploy_ioc_vars.py` | Device role vars files are valid YAML with expected keys |
| `test_device_roles.py` | Every device role has a corresponding vars file |
| `test_validate_ex_configs_against_schemas.py` | Example configs pass their role's schema validation |

## Linting

```bash
# Lint all files
pixi run lint

# Lint only changed files (faster, uses pre-commit)
pixi run lint-changes

# Auto-fix Python linting issues
pixi run ruff-fix
```

## Troubleshooting

### Container Won't Start

```bash
# Remove existing container and retry
docker container rm -f epics-dev
docker pull ghcr.io/nsls2/epics-alma8:latest
docker run -dit --name epics-dev ghcr.io/nsls2/epics-alma8:latest
```

### Module Compilation Fails

- Check the module's `pkg_deps` — missing development libraries cause build failures
- Run with `--verbose` for detailed Ansible output
- Inspect the container: `docker exec -it epics-dev bash`

### Schema Validation Errors

If `test_validate_ex_configs_against_schemas.py` fails:

- Ensure your `example.yml` matches the `schema.yml` exactly
- Check for typos in field names
- Verify `type` field matches the role name
