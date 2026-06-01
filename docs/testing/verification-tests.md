# Writing Verification Tests

Verification tests allow you to validate the structure and content of deployed IOC files after a deployment completes. They use a declarative `verify.yml` schema that is checked by the `scripts/verify_deployment.py` script.

## Overview

A `verify.yml` file defines what the deployed IOC directory should look like:

- Which files must exist
- What content files must contain
- What content files must NOT contain (e.g., unrendered Jinja2 templates)
- Expected file permissions

## File Location

Place `verify.yml` alongside your example configuration:

```
roles/device_roles/mydevice/
└── examples/
    └── my-example/
        ├── config.yml       # IOC configuration
        └── verify.yml       # Verification schema
```

## Schema Structure

```yaml
---
# Whether to skip module compilation during testing
skip_compilation: false

verification:
  files_must_exist:
    - path/to/file1
    - path/to/file2

  file_must_contain:
    path/to/file:
      - "expected string 1"
      - "expected string 2"

  file_must_not_contain:
    path/to/file:
      - "forbidden string"

  permissions:
    path/to/file: "0775"
```

All paths are relative to the IOC directory (e.g., `iocBoot/st.cmd`).

## Fields

### `skip_compilation`

- **Type**: boolean
- **Required**: yes
- **Description**: Set to `true` for roles that require proprietary SDKs not available in CI. When true, module compilation is skipped during testing, and only the file structure is validated.

### `verification.files_must_exist`

- **Type**: list of strings
- **Description**: Files that must be present after deployment. Checks existence only.

```yaml
files_must_exist:
  - iocBoot/st.cmd
  - iocBoot/epicsEnv.cmd
  - iocBoot/base.cmd
  - iocBoot/postInit.cmd
  - as/req/auto_settings.req
```

### `verification.file_must_contain`

- **Type**: dict mapping filenames to lists of strings
- **Description**: Each file must contain ALL listed strings as substrings.

```yaml
file_must_contain:
  iocBoot/st.cmd:
    - "iocInit"
    - "epicsEnvSet"
  iocBoot/base.cmd:
    - "dbLoadRecords"
    - "myDriverConfig"
```

### `verification.file_must_not_contain`

- **Type**: dict mapping filenames to lists of strings (optional)
- **Description**: Files must NOT contain any of the listed strings. Commonly used to detect unrendered Jinja2 templates.

```yaml
file_must_not_contain:
  iocBoot/st.cmd:
    - "{{"    # No unrendered Jinja2 variables
    - "}}"
  iocBoot/base.cmd:
    - "{{"
    - "}}"
  iocBoot/epicsEnv.cmd:
    - "{{"
    - "}}"
```

!!! tip
    Always check for `{{` and `}}` in your generated files. This catches cases where Jinja2 variables weren't properly resolved during deployment.

### `verification.permissions`

- **Type**: dict mapping filenames to octal permission strings
- **Description**: Validates file permissions match expected values.

```yaml
permissions:
  iocBoot/st.cmd: "0775"     # Executable
  iocBoot/base.cmd: "0664"   # Read/write for owner+group
```

## Complete Example

From `adsimdetector`:

```yaml
---
skip_compilation: false

verification:
  files_must_exist:
    # Standard IOC boot files (created by deploy_ioc)
    - iocBoot/st.cmd
    - iocBoot/epicsEnv.cmd
    - iocBoot/postInit.cmd
    # Role-specific files
    - iocBoot/base.cmd
    - as/req/auto_settings.req

  file_must_contain:
    iocBoot/st.cmd:
      - "iocInit"
    iocBoot/base.cmd:
      - "simDetectorConfig"
      - "dbLoadRecords"
      - "simDetector.template"
    as/req/auto_settings.req:
      - "simDetector_settings.req"
      - "commonPlugin_settings.req"

  file_must_not_contain:
    iocBoot/st.cmd:
      - "{{"
      - "}}"
    iocBoot/base.cmd:
      - "{{"
      - "}}"
    iocBoot/epicsEnv.cmd:
      - "{{"
      - "}}"

  permissions:
    iocBoot/st.cmd: "0775"
```

## Validation Schema

The `verify.yml` files themselves are validated against `schemas/verify.yml`:

```yaml
skip_compilation: bool()

verification:
  files_must_exist: list(str())
  file_must_contain: map(list(str()), key=str())
  file_must_not_contain: map(list(str()), key=str(), required=False)
  permissions: map(str(), key=str())
```

## Best Practices

1. **Always check for unrendered Jinja2** — Add `file_must_not_contain` checks for `{{` and `}}` in all generated files.
2. **Check key functional content** — Verify that important commands (driver config, database loading, `iocInit`) appear in the right files.
3. **Test permissions on executables** — `st.cmd` should always be `0775`.
4. **Keep patterns stable** — Use content checks that won't break when environment variables change (e.g., check for the function name, not the full line with variable values).
5. **Set `skip_compilation` honestly** — Only skip when hardware/SDK dependencies truly prevent compilation in CI.
