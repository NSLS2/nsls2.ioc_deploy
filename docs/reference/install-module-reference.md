# install_module Reference

The `install_module` role compiles EPICS modules from source with automatic dependency resolution. It manages the entire build process from cloning repositories to generating configuration files and running compilation.

## How It Works

EPICS doesn't have a built-in dependency solver, so compatible versions must be explicitly described in configuration files. Each module has a vars file in `roles/install_module/vars/` that pins a specific git commit and lists its dependencies.

The role:

1. Builds a dependency tree with the target module as a leaf
2. Resolves transitive dependencies automatically
3. Clones each dependency and checks out the specified commit
4. Generates `RELEASE` and `CONFIG_SITE` files from templates
5. Compiles modules top-down (dependencies before dependents)
6. Sets proper file ownership

## Module Configuration File

Each module is defined by a YAML file in `roles/install_module/vars/`. The file must be named `{module_name}_{version}.yml`.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Human-readable module name (e.g., `"ADVimba"`) |
| `url` | string | Git clone URL |
| `version` | string | Git commit hash (7-40 hex characters) |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `include_base_ad_config` | bool | `false` | Include standard areaDetector build config |
| `module_deps` | list | `[]` | Other modules to build first (by config name) |
| `pkg_deps` | list | `["epics-bundle"]` | System packages to install |
| `config` | dict | `{}` | Custom CONFIG_SITE values |
| `executable` | string | — | IOC executable name within the module |
| `compilation_command` | string | `"make -sj"` | Custom build command |
| `use_token` | bool | `false` | Use auth token for private repos |

### Example: Standard Module

```yaml
---

motorsim_d1d0eb8:
  name: MotorSim
  url: https://github.com/epics-motor/motorMotorSim
  version: d1d0eb8
```

### Example: areaDetector Module

```yaml
---

adaravis_a0aa4d6:
  name: ADAravis
  url: https://github.com/areaDetector/ADAravis
  include_base_ad_config: true
  version: a0aa4d6
  executable: ADAravisApp
  module_deps:
    - adgenicam_5d08a11
```

### Example: Module with Custom Config

```yaml
---

mymodule_abc1234:
  name: MyModule
  url: https://github.com/org/MyModule
  version: abc1234
  config:
    WITH_FEATURE_X: "YES"
    CUSTOM_LIB_DIR: "/opt/custom/lib"
  pkg_deps:
    - epics-bundle
    - custom-devel
  compilation_command: "cd iocs/myIOC && make -sj"
```

## Role Defaults

### `install_module_install_dir`

- **Default**: `"/epics/modules"`
- **Description**: Base directory for compiled modules. Each module is installed in a subdirectory named after its config (e.g., `/epics/modules/adaravis_a0aa4d6/`).

### `install_module_default_compilation_command`

- **Default**: `"make -sj"`
- **Description**: Default build command. `-s` for silent, `-j` for parallel jobs.

### `install_module_force_reinstall`

- **Default**: `false`
- **Description**: Force recompilation even if the module directory already exists.

### `install_module_skip_compilation`

- **Default**: `false`
- **Description**: Skip the actual compilation step. Useful in CI for roles that require proprietary SDKs.

### `install_module_default_pkg_deps`

- **Default**: `["epics-bundle"]`
- **Description**: System packages installed before compilation.

### `install_module_default_epics_deps`

Standard EPICS module paths provided by `epics-bundle`:

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

### `install_module_default_config_dict`

Default `CONFIG_SITE` values for all modules:

```yaml
CHECK_RELEASE: 'NO'
BUILD_IOCS: 'YES'
```

### `install_module_ad_config_dict`

Extended configuration applied when `include_base_ad_config: true`:

```yaml
WITH_BOOST: 'NO'
WITH_PVA: 'YES'
WITH_QSRV: 'YES'
WITH_BLOSC: 'YES'
WITH_BITSHUFFLE: 'YES'
WITH_GRAPHICSMAGICK: 'YES'
WITH_HDF5: 'YES'
WITH_JSON: 'YES'
WITH_JPEG: 'YES'
WITH_NETCDF: 'YES'
WITH_NEXUS: 'YES'
WITH_OPENCV: 'NO'
WITH_SZIP: 'YES'
WITH_TIFF: 'YES'
WITH_ZLIB: 'YES'
# ... plus EXTERNAL flags and library paths
```

## Dependency Resolution

Only specify **immediate** parent dependencies in `module_deps`. The role resolves transitive dependencies automatically.

For example, if you have:

```
ADAravis → ADGenICam → ADCore → ADSupport
```

The `adaravis` config only needs to list `adgenicam_5d08a11`. The role follows the chain to discover `adcore` and `adsupport` automatically.

## Schema Validation

Module configs are validated against `schemas/install_module.yml`:

```yaml
name: str()
url: url()
version: git_commit_hash()
include_base_ad_config: bool(required=False)
module_deps: list(module_name(), required=False)
pkg_deps: list(str(), required=False)
config: map(str(), key=str(), required=False)
use_token: bool(required=False)
executable: str(required=False)
compilation_command: str(required=False)
```

The `module_name()` validator ensures all referenced dependencies actually exist as vars files.
