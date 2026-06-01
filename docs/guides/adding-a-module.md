# Adding a New Module

This guide walks through adding a new installable EPICS module to the collection. A "module" is an EPICS support module that can be compiled from source and made available for IOC deployments.

## When to Add a Module

Add a module when:

- You need an EPICS support module that isn't provided by the `epics-bundle` RPM
- Your device role requires a specific version of a module
- You need a module as a dependency for another module

## Interactive Method (Recommended)

The simplest way to add a module:

```bash
pixi run make-module
```

This will prompt you for:

1. **Module name** — The human-readable name (e.g., `ADKinetix`)
2. **Git commit hash** — The specific version to pin (e.g., `aa87406`)
3. **Git URL** — The repository URL (e.g., `https://github.com/NSLS2/ADKinetix`)
4. **areaDetector module?** — Whether to include AD build configuration
5. **Module dependencies** — Select any required modules from the existing list

The script creates the configuration file at `roles/install_module/vars/<name>_<version>.yml`.

## Manual Method

### Step 1: Identify the Module Version

Choose a specific git commit hash for reproducibility. Avoid using branch names or tags, as these can change unexpectedly.

```bash
# Clone the module repo and identify the desired commit
git clone https://github.com/org/MyModule.git
cd MyModule
git log --oneline -5
# Pick a commit hash, e.g., abc1234
```

### Step 2: Create the Configuration File

Create `roles/install_module/vars/mymodule_abc1234.yml`:

```yaml
---

mymodule_abc1234:
  name: MyModule
  url: https://github.com/org/MyModule
  version: abc1234
```

!!! warning "File naming convention"
    The filename **must** match the top-level key: `{name_lowercase}_{version}.yml`

### Step 3: Add Dependencies (if needed)

If the module depends on other modules that need to be compiled:

```yaml
---

mymodule_abc1234:
  name: MyModule
  url: https://github.com/org/MyModule
  version: abc1234
  module_deps:
    - asyn_abc1234  # Must reference an existing vars file
```

Only specify **immediate** dependencies. Transitive dependencies are resolved automatically.

### Step 4: Add Custom Build Configuration (if needed)

For modules that require non-default build options:

```yaml
---

mymodule_abc1234:
  name: MyModule
  url: https://github.com/org/MyModule
  version: abc1234
  config:
    WITH_CUSTOM_FEATURE: "YES"
    CUSTOM_LIB: "/opt/custom"
  pkg_deps:
    - epics-bundle
    - libcustom-devel
  compilation_command: "cd myIOCApp && make -sj"
```

### Step 5: Add the Executable Name (if applicable)

If the module builds a runnable IOC application:

```yaml
---

mymodule_abc1234:
  name: MyModule
  url: https://github.com/org/MyModule
  version: abc1234
  executable: myModuleApp
```

## Validation

Run the test suite to validate your new module configuration:

```bash
pixi run tests tests/test_install_module_vars.py
```

The tests verify:

- The file conforms to `schemas/install_module.yml`
- The top-level key matches the filename
- All referenced `module_deps` exist as vars files
- The URL is valid
- The version matches the git commit hash format

## Using the Module in a Device Role

Once your module exists, you can reference it in a device role's vars file (`roles/deploy_ioc/vars/<type>.yml`):

```yaml
---

deploy_ioc_required_module: mymodule_abc1234
deploy_ioc_executable: myModuleApp
deploy_ioc_template_root_path: "{{ deploy_ioc_required_module_path }}"
```

## Updating a Module Version

To update an existing module to a new version:

```bash
pixi run update-module
```

This will:

1. Prompt you to select the module to update
2. Ask for the new git commit hash
3. Create a new vars file with the updated version
4. Update all references in other module deps and device role vars
5. Optionally delete the old configuration file

## Deleting a Module

```bash
pixi run delete-module
```

!!! note
    A module cannot be deleted if it is referenced by other modules' `module_deps` or by any device role's `deploy_ioc_required_module`.
