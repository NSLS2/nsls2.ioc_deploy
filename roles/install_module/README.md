# Install Module

## Overview

The `install_module` role is responsible for ensuring that required EPICS software modules are available on the target host during deployment. It provides intelligent compilation and dependency resolution for EPICS modules that don't ship with the standard `epics-bundle` distribution.

### Key Responsibilities

- Builds dependency trees with automatic recursive resolution
- Clones git repositories and checks out specified versions (tags or commits)
- Generates EPICS `RELEASE` and `CONFIG_SITE` files from templates
- Compiles modules with configurable build commands
- Manages system package dependencies (via dnf/yum)
- Ensures proper file ownership for compiled modules
- Handles both standard EPICS modules and Area Detector modules with specialized configurations

### How It Works

Because EPICS doesn't have a built-in dependency solver, compatible versions must be explicitly described in configuration files. Each module supported by this role has one or more configuration files (in `vars/`) that describe a specific version and its dependencies.

The role builds a dependency tree with the target module as a leaf and compiles all modules from the top down. You only need to specify immediate parent dependencies; the role handles transitive dependencies automatically. Unless otherwise stated, the `epics-bundle` package provides baseline dependencies.

Once a dependency list is established, the role:
1. Clones and checks out the correct version of each module
2. Finds and removes existing `RELEASE` and `CONFIG_SITE` files
3. Auto-generates new configuration files from Jinja templates
4. Runs the compilation command (default: `make -sj`)
5. Sets proper ownership on all compiled files

## Required Input Variables

When using this role, the following variables must be provided:

### Host Configuration

**`host_config`** (dict, required)

The host configuration dictionary containing system-level settings. Must include:

- `epics_interface.address`: IP address for EPICS Channel Access interface
- `epics_interface.broadcast`: Broadcast address for EPICS Channel Access
- `softioc_user`: User account that will own compiled module files
- `softioc_group`: Group that will own compiled module files

### Module Specification

**`install_module_name`** (string, required)

The name of the module to install, matching a configuration file in `vars/`. Format: `{module_name}_{version}` (e.g., `motorsim_d1d0eb8`, `advimba_34686fe`).

## Module Configuration File Structure

Each module is defined by a YAML configuration file in the `vars/` directory. These files describe the module's source, version, dependencies, and build configuration.

### File Naming Convention

Configuration files should be named: `{module_name}_{version}.yml`

- Use the short git commit hash (7 characters)
- Example: `advimba_34686fe.yml`, `motorsim_d1d0eb8.yml`

### Configuration File Fields

See `schemas/install_module.yml` for the complete validation schema.

**Required Fields:**

**`name`** (string, required)
- Human-readable name of the module (e.g., "ADVimba", "MotorSim")

**`url`** (string, required)
- Public git URL from which to clone the module
- Example: `https://github.com/areaDetector/ADVimba`

**`version`** (string, required)
- Git tag, commit hash, or branch to check out
- **Recommended**: commit hashes for reproducibility
- **Not recommended**: Branches or tags (unpredictable)
- Must match the version in the file name

**Optional Fields:**

**`epics_deps`** (dict, optional)
- EPICS module dependencies provided by `epics-bundle` (not built by this role)
- Maps module names to their installation paths
- Default: Inherits from `install_module_default_epics_deps`
- Typically set to `/usr/lib/epics` for bundle-provided modules

**`pkg_deps`** (list, optional)
- System packages to install via dnf/yum
- Default: `["epics-bundle"]`
- Add additional packages as needed (e.g., development libraries)

**`include_base_ad_config`** (boolean, optional)
- Set to `true` for Area Detector modules
- Includes comprehensive AD configuration from `install_module_ad_config_dict`
- Handles HDF5, JPEG, TIFF, netCDF, GraphicsMagick, and other AD features

**`config`** (dict, optional)
- Custom CONFIG_SITE values (e.g., `TIRPC: "YES"`, `WITH_XXX: "YES"`)
- Overrides default configuration values
- Merged with `install_module_default_config_dict` and optionally `install_module_ad_config_dict`

**`module_deps`** (list, optional)
- Additional EPICS modules to be built by this role
- Only specify immediate parent dependencies (transitive deps are resolved automatically)
- Reference by configuration file name (e.g., `adgenicam_5d08a11`)

**`compilation_command`** (string, optional)
- Custom build command if not a simple top-level make
- Default: `make -sj`
- Example: `cd subdir && make -sj`

**`executable`** (string, optional)
- Path to the IOC executable within the compiled module
- Used when the module includes a runnable IOC application
- Example: `"vimbaApp"`

**`use_token`** (boolean, optional)
- Whether to use authentication token for private repositories
- Requires token configuration in the calling playbook

### Example Module Configuration

```yaml
advimba_34686fe:
  name: ADVimba
  url: https://github.com/areaDetector/ADVimba
  version: 34686fe

  # Area Detector module - include standard AD configuration
  include_base_ad_config: true

  # Depends on ADGenICam (which will be built if not already installed)
  module_deps:
    - adgenicam_5d08a11

  # Will use epics-bundle for base EPICS modules (inherited from defaults)
  # Will compile with "make -sj" (inherited from defaults)

  # Specify the executable path for IOC deployment
  executable: "vimbaApp"
```

### Minimal Module Configuration

```yaml
motorsim_d1d0eb8:
  name: MotorSim
  url: https://github.com/epics-motor/motorMotorSim
  version: d1d0eb8

  # Uses all defaults:
  # - epics-bundle for dependencies
  # - Standard compilation command
  # - No module dependencies
```

## Role Variables

The following variables can be overridden to customize the installation behavior. These are defined in `defaults/main.yml`.

### Installation Configuration

**`install_module_install_dir`**
- **Type**: string
- **Default**: `"/epics/modules"`
- **Description**: Directory where compiled EPICS modules are installed. Each module is installed in a subdirectory named after the module configuration.

**`install_module_default_compilation_command`**
- **Type**: string
- **Default**: `"make -sj"`
- **Description**: Default command used to compile modules. The `-sj` flags enable silent mode and parallel compilation. Can be overridden per-module via the `compilation_command` field.

**`install_module_force_reinstall`**
- **Type**: boolean
- **Default**: `false`
- **Description**: Whether to force reinstallation even if the module already exists. When true, performs a hard reset of the git repository.

### Package Dependencies

**`install_module_default_pkg_deps`**
- **Type**: list
- **Default**: `["epics-bundle"]`
- **Description**: Default system packages required for module compilation. The `epics-bundle` package provides EPICS Base and common support modules. Individual modules can extend this list via `pkg_deps`.

### EPICS Dependencies

**`install_module_default_epics_deps`**
- **Type**: dict
- **Default**: See below
- **Description**: Default paths to EPICS modules provided by `epics-bundle`. These modules are not compiled by the role but are referenced in generated RELEASE files.

Default EPICS dependencies:

```yaml
ASYN: /usr/lib/epics
AUTOSAVE: /usr/lib/epics
BUSY: /usr/lib/epics
CALC: /usr/lib/epics
DEVIOCSTATS: /usr/lib/epics
SSCAN: /usr/lib/epics
STREAM: /usr/lib/epics
SNCSEQ: /usr/lib/epics
RECCASTER: /usr/lib/epics
MOTOR: /usr/lib/epics
EPICS_BASE: /usr/lib/epics
```

### Build Configuration

**`install_module_default_config_dict`**
- **Type**: dict
- **Default**: See below
- **Description**: Default CONFIG_SITE values applied to all modules. These control EPICS build behavior.

Default configuration:

```yaml
CHECK_RELEASE: 'NO'      # Disable EPICS release file checking (conflicts with overrides)
BUILD_IOCS: 'YES'        # Build example IOCs by default
```

**`install_module_ad_config_dict`**
- **Type**: dict
- **Default**: See below
- **Description**: Comprehensive Area Detector configuration applied when `include_base_ad_config: true`. Controls which plugins and external libraries are enabled for AD modules.

Area Detector configuration includes settings for:
- **PVA/QSRV**: PV Access and QSR server support
- **Image Formats**: HDF5, JPEG, TIFF, netCDF, Nexus
- **Compression**: Blosc, Bitshuffle, szip, zlib
- **Processing**: GraphicsMagick, OpenCV
- **Camera Interfaces**: Aravis (GigE Vision), GLib

Key settings:

```yaml
WITH_PVA: 'YES'                      # Enable PV Access support
WITH_QSRV: 'YES'                     # Enable PV Access server
WITH_HDF5: 'YES'                     # Enable HDF5 file plugin
WITH_JPEG: 'YES'                     # Enable JPEG support
WITH_TIFF: 'YES'                     # Enable TIFF support
WITH_GRAPHICSMAGICK: 'YES'           # Enable GraphicsMagick for format conversion
WITH_BLOSC: 'YES'                    # Enable Blosc compression
WITH_NETCDF: 'YES'                   # Enable netCDF file format
WITH_NEXUS: 'YES'                    # Enable Nexus file format
WITH_OPENCV: 'NO'                    # Disable OpenCV by default
ARAVIS_LIB: /usr/lib64               # Aravis library location
ARAVIS_INCLUDE: /usr/include/aravis-0.8
GLIB_INCLUDE: /usr/include/glib-2.0 /usr/lib64/glib-2.0/include
```

Most external dependencies use `_EXTERNAL: 'NO'` to indicate they should be built from AD's vendored sources rather than system libraries. This ensures compatibility across different target systems.

## Adding a New Module

To add a module to `install_module`, create a single YAML configuration file in the `vars/` directory following the structure documented above.

### Step-by-Step Process

1. **Determine module information:**
   - Git repository URL
   - Specific version (tag or commit hash)
   - Immediate EPICS module dependencies
   - System package dependencies
   - Any custom build configuration needed

2. **Create configuration file:**
   - Name: `vars/{module_name}_{version}.yml`
   - Include all required fields: `name`, `url`, `version`
   - Add optional fields as needed
   - For Area Detector modules, set `include_base_ad_config: true`

3. **Handle dependencies:**
   - If the module depends on other custom modules (not in epics-bundle), add them to `module_deps`
   - If the module requires special system libraries, add them to `pkg_deps`
   - If the module needs specific EPICS modules from epics-bundle, they're typically covered by defaults

4. **Test the configuration:**
   - Run the role with your new module
   - Verify compilation succeeds
   - Check that dependencies are correctly resolved

### Example: Adding a New Area Detector Camera

```yaml
adnewcamera_abc1234:
  name: ADNewCamera
  url: https://github.com/areaDetector/ADNewCamera
  version: abc1234

  # Enable Area Detector configuration
  include_base_ad_config: true

  # Depends on ADGenICam and ADSupport
  module_deps:
    - adgenicam_5d08a11

  # Requires vendor SDK from system packages
  pkg_deps:
    - vendor-camera-sdk-devel

  # Custom configuration for vendor SDK paths
  config:
    VENDOR_SDK_LIB: /usr/lib64
    VENDOR_SDK_INCLUDE: /usr/include/vendor-camera

  # Executable for IOC deployment
  executable: "newCameraApp"
```

## Output Variables

After running the role, the following variables are set and can be used by subsequent tasks:

**`install_module_installed`**
- **Type**: dict
- **Description**: Maps uppercase module names to their installation paths

**`install_module_installed_list`**
- **Type**: list
- **Description**: List of all module names installed during this run

**`install_module_leaf_module_path`**
- **Type**: string
- **Description**: Path to the final (leaf) module that was requested

**`install_module_leaf_executable`**
- **Type**: string
- **Description**: Executable path for the leaf module (if specified in configuration)

## Usage Examples

### Installing a Single Module

```yaml
- name: Install MotorSim module
  ansible.builtin.include_role:
    name: nsls2.ioc_deploy.install_module
  vars:
    install_module_name: motorsim_d1d0eb8
```

### Installing with Force Reinstall

```yaml
- name: Force reinstall ADVimba
  ansible.builtin.include_role:
    name: nsls2.ioc_deploy.install_module
  vars:
    install_module_name: advimba_34686fe
    install_module_force_reinstall: true
```

### Custom Installation Directory

```yaml
- name: Install module to custom location
  ansible.builtin.include_role:
    name: nsls2.ioc_deploy.install_module
  vars:
    install_module_name: motorsim_d1d0eb8
    install_module_install_dir: /opt/epics/modules
```

## Notes

- **Dependency Resolution**: The role automatically resolves transitive dependencies. You only need to specify immediate parent dependencies in `module_deps`.
- **epics-bundle Integration**: Modules from `epics-bundle` are used as-is from `/usr/lib/epics` and are not compiled by this role.
- **Area Detector Modules**: Always set `include_base_ad_config: true` for AD modules to ensure proper plugin configuration.
- **EPICS Base**: The `epics_base` module is handled specially with recursive git clones and no RELEASE/CONFIG_SITE modifications.
