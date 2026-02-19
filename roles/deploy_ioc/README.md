# Deploy IOC

## Overview

The `deploy_ioc` role is the main central role that performs all common operations for EPICS IOC deployment at NSLS-II. It automates the deployment of EPICS IOCs with a standardized directory structure, startup scripts, and optional systemd service configuration.

### Key Responsibilities

- Creates standardized IOC directory structure (`db/`, `iocBoot/`, `as/`, etc.)
- Generates EPICS startup scripts (`st.cmd`, `epicsEnv.cmd`, `common.cmd`, `postInit.cmd`)
- Processes IOC substitutions and generates database files
- Deploys network configuration for EPICS Channel Access
- Generates manage-iocs configuration files for systemd service management
- Coordinates with device-specific roles in `device_roles/` to deploy hardware-specific configurations
- Optionally installs, enables, and starts IOC services via systemd

This role is designed to work in conjunction with device-specific roles (e.g., `device_roles.tetramm`, `device_roles.motorsim`) that provide hardware-specific templates and configurations.

## Required Input Variables

When using this role, the following variables must be provided by the calling playbook or inventory:

### Host Configuration

**`host_config`** (dict, required)

The host configuration dictionary containing system-level settings. Must include:

- `epics_interface.address`: IP address for EPICS Channel Access interface
- `epics_interface.broadcast`: Broadcast address for EPICS Channel Access
- `softioc_user`: User account that will own and run the IOC
- `softioc_group`: Group that will own IOC files

### IOC Configuration

**`ioc`** (dict, required)

The IOC configuration dictionary for the specific IOC being deployed. See `schema.yml` for the complete structure. Key fields include:

- `type`: IOC type/device driver (e.g., "tetramm", "motorsim")
- `environment`: Dict of environment variables specific to this IOC
- `substitutions`: Dict of database substitutions to load
- `executable`: (optional) Custom IOC executable
- `simulation`: (optional) Boolean to enable simulation mode
- `dbpf`: (optional) List of database put-field commands to execute at startup

**`deploy_ioc_ioc_name`** (string, required)

The name of the IOC being deployed. This is typically set automatically by the role when iterating over IOCs.

**`deploy_ioc_target`** (string, required)

Specifies which IOCs to deploy. Can be:
- `"all"`: Deploy all IOCs found in host_config
- Comma-separated list: Deploy specific IOCs (e.g., `"ioc1,ioc2"`)

## Role Variables

The following variables can be overridden to customize the deployment behavior. These are defined in `defaults/main.yml`.

### Directory Configuration

**`deploy_ioc_base_directory`**
- **Type**: string
- **Default**: `"/epics"`
- **Description**: Base directory for all EPICS-related files and IOCs.

**`deploy_ioc_common_directory`**
- **Type**: string
- **Default**: `"{{ deploy_ioc_base_directory }}/common"`
- **Description**: Directory for common EPICS files shared across IOCs, such as network setup configuration files.

**`deploy_ioc_template_root_path`**
- **Type**: string
- **Default**: `"/usr/lib/epics"`
- **Description**: Root path where EPICS modules and templates are installed. Used as the base for locating support modules.

**`deploy_ioc_iocs_directory`**
- **Type**: string
- **Default**: `"{{ deploy_ioc_base_directory }}/iocs"`
- **Description**: Parent directory where all IOC instances are deployed.

**`deploy_ioc_ioc_directory`**
- **Type**: string
- **Default**: `"{{ deploy_ioc_iocs_directory }}/{{ deploy_ioc_ioc_name }}"`
- **Description**: Full path to the specific IOC directory being deployed. Automatically constructed from parent directory and IOC name.

**`deploy_ioc_as_dir_name`**
- **Type**: string
- **Default**: `"as"`
- **Description**: Name of the autosave directory within the IOC directory.

**`deploy_ioc_as_directory`**
- **Type**: string
- **Default**: `"{{ deploy_ioc_ioc_directory }}/{{ deploy_ioc_as_dir_name }}"`
- **Description**: Full path to the autosave directory containing `req/` and `save/` subdirectories.

### IOC Deployment Behavior

**`deploy_ioc_executable`**
- **Type**: string
- **Default**: `"softIoc"`
- **Description**: The EPICS IOC executable to use. Should be overridden by most device roles.

**`deploy_ioc_standard_st_cmd`**
- **Type**: boolean
- **Default**: `true`
- **Description**: Whether to generate standard EPICS startup scripts and directory structure. Set to false for IOCs with completely custom startup procedures.

**`deploy_ioc_use_common`**
- **Type**: boolean
- **Default**: `true`
- **Description**: Whether to include `common.cmd` in the IOC startup script. The common.cmd file loads frequently-used EPICS modules.

**`deploy_ioc_use_ad_common`**
- **Type**: boolean
- **Default**: `false`
- **Description**: Whether to use Area Detector common configuration. Set to true for Area Detector-based IOCs.

**`deploy_ioc_load_as_substitutions`**
- **Type**: boolean
- **Default**: `true`
- **Description**: Whether to process and load database substitutions defined in the IOC configuration. Device roles should set this to false if they handle substitutions manually.

**`deploy_ioc_post_deploy_step`**
- **Type**: string
- **Default**: `"None"`
- **Description**: Action to perform after deployment. Options: `"None"`, `"Install"`, `"Install and Enable"`, `"Install and Start"`, `"Install and Enable and Start"`, `"Restart"`.

**`deploy_ioc_nextport`**
- **Type**: integer
- **Default**: `4000`
- **Description**: Starting port number for IOC services (e.g., procServ telnet port). Automatically incremented for multiple IOCs.

### Autosave Configuration

**`deploy_ioc_make_autosave_files`**
- **Type**: boolean
- **Default**: `false`
- **Description**: Whether to automatically generate autosave request files. When true, creates `.req` files from the IOC's PV list.

**`deploy_ioc_req_file_list`**
- **Type**: list
- **Default**: `[]`
- **Description**: List of autosave request files to copy or reference. Used when autosave configuration is managed by the device role.

### Database Configuration

**`deploy_ioc_dbpf_list`**
- **Type**: list
- **Default**: `[]`
- **Description**: List of database put-field (dbpf) commands to execute during IOC initialization. Each entry should specify PV name and value.

### Environment Variables

**`deploy_ioc_os_env_exports`**
- **Type**: dict
- **Default**: `{}`
- **Description**: Operating system environment variables to export before starting the IOC. Used for system-level configuration that doesn't belong in EPICS environment.

**`deploy_ioc_device_specific_env`**
- **Type**: dict
- **Default**: `{}`
- **Description**: Device-specific environment variables that override or extend the default EPICS environment. Merged with `deploy_ioc_default_env`.

**`deploy_ioc_default_env`**
- **Type**: dict
- **Default**: See below
- **Description**: Default EPICS environment variables available to all IOCs. Includes paths to EPICS base and common support modules.

Default environment variables include:

```yaml
IOC: "{{ ioc.type }}"
IOC_DIR: "{{ deploy_ioc_iocs_directory }}"
TOP: "$(IOC_DIR)/{{ deploy_ioc_ioc_name }}"
TEMPLATE_TOP: "{{ deploy_ioc_template_root_path }}"
HOSTNAME: "{{ inventory_hostname.split('.')[0] }}"
IOCNAME: "{{ deploy_ioc_ioc_name }}"

# EPICS module paths. By default all versions are pulled from central RPM distribution.
# Add module dep to device role or ioc instance if specific versions are needed.
ASYN: /usr/lib/epics
AUTOSAVE: /usr/lib/epics
BUSY: /usr/lib/epics
CALC: /usr/lib/epics
DEVIOCSTATS: /usr/lib/epics
SSCAN: /usr/lib/epics
STREAM: /usr/lib/epics
SNCSEQ: /usr/lib/epics
RECCASTER: /usr/lib/epics
EPICS_BASE: /usr/lib/epics
```

### System Configuration

**`deploy_ioc_required_system_packages`**
- **Type**: list
- **Default**: `["procServ"]`
- **Description**: List of system packages required for IOC operation. These packages are automatically installed via dnf/yum during deployment.

## Usage for Device Role Developers

When creating a new device role, you can rely on the `deploy_ioc` role to handle:

1. **Directory Structure**: Standard directories (`db/`, `iocBoot/`, `as/req/`, `as/save/`) are created automatically
2. **Startup Scripts**: Base startup scripts are generated; you can add device-specific commands via templates
3. **Substitution Processing**: Set `deploy_ioc_load_as_substitutions: true` and define substitutions in the IOC config
4. **Environment Variables**: Extend `deploy_ioc_device_specific_env` in your device role's `vars/<role-name>.yml` for device-specific paths
5. **Service Management**: The role handles systemd service generation and management based on `deploy_ioc_post_deploy_step`

Your device role should focus on:
- Device-specific templates and configuration files
- Custom database files or substitution patterns
- Hardware initialization commands
- Driver-specific environment variables

See existing overrides for device configurations in `vars/` for examples.
