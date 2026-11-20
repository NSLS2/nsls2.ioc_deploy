# base_soft_ioc

Deploys a generic EPICS soft IOC with no device support, for serving user-provided databases loaded via substitutions files. The IOC is built from [BaseSoftIOC](https://github.com/NSLS2/BaseSoftIOC) (version `f4c87af`).

## Example Configuration

Taken from [`examples/base-soft-ioc-01/config.yml`](examples/base-soft-ioc-01/config.yml) (the example directory also provides `test.db` and `test.substitutions`):

```yaml
base-soft-ioc-01:
  type: base_soft_ioc
  environment:
    ENGINEER: C. Engineer
    SYS: TEST
    DEV: "{PRM:VAR}"
    PREFIX: "$(SYS)$(DEV)"
    CT_PREFIX: "$(SYS){IOC:1}"

  # In this example the database 'test.db' is loaded in 3 ways:
  #   1. test.substitutions file is copied to the $(TOP)/db
  #      directory and automatically loaded in common.cmd file.
  #      All variables must be defined in the .substitutions
  #      file, there is no way to pass parameters from the .cmd
  #      file.
  substitutions:
    # 2: test-gen-fixed-params.substitutions file is generated
    #    automatically based on the parameters specified under 'templates'
    #    key. No parameters are passed from the .cmd file in the
    #    dbLoadTemplate function.
    test-gen-fixed-params:
      templates:
        - filepath: "$(TOP)/db/test.db"
          pattern: ["P", "R"]
          instances:
            - ["TEST", "{PRM:FIXED}"]
    # 3. test-gen-variable-params.substitutions file is generated
    #    based on the parameters under the 'templates' key.
    #    The 'template_macros' is a string that is included as the second
    #    argument of dbLoadTemplate function. In this example the parameter
    #    'P' is passed directly to the test.db file. The parameter 'DEV'
    #    is passed to the substitution file and used to set the 'R' parameter.
    #    (The generated substitutions file will contain "$(DEV)" as a value
    #    for the instance)
    test-gen-variable-params:
      template_macros: "P=$(SYS),DEV=$(DEV)"
      templates:
        - filepath: "$(TOP)/db/test.db"
          pattern: ["R"]
          instances:
            - ["$(DEV)"]
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `base_soft_ioc`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | General PV prefix; may reference other macros (e.g. `$(SYS)$(DEV)`). Used for IOC-specific PVs only if `CT_PREFIX` is not set. |
| `environment.SYS` | Yes | - | System portion of the PV prefix, available as a macro for substitutions. |
| `environment.DEV` | Yes | - | Device portion of the PV prefix, available as a macro for substitutions. |
| `environment.CT_PREFIX` | Yes | - | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster); takes precedence over `PREFIX`. |
| `substitutions` | No | - | Map of substitutions file name to its contents. Each entry generates `$(TOP)/db/<name>.substitutions`, loaded with `dbLoadTemplate` in `common.cmd`. The value is either a list of templates or a map with `templates` and optional `template_macros`. |
| `substitutions.<name>.templates` | No | - | List of templates in the generated substitutions file. |
| `substitutions.<name>.templates[].filepath` | Yes | - | Path of the database/template file (e.g. `$(TOP)/db/test.db`). |
| `substitutions.<name>.templates[].pattern` | Yes | - | List of macro names forming the substitutions `pattern` row. |
| `substitutions.<name>.templates[].instances` | Yes | - | List of instances; each is a list of values matching `pattern`. |
| `substitutions.<name>.template_macros` | No | - | Macro string passed as the second argument to `dbLoadTemplate` (e.g. `"P=$(SYS),DEV=$(DEV)"`). |

## Notes

- `base.cmd` only loads the `baseSoftIOC` dbd; all records come from `substitutions` and/or manually provided files (`deploy_ioc_manual_ioc_files`). `.db`/`.substitutions` files are placed in `$(TOP)/db`, and any `.substitutions` file not named in `substitutions` is loaded automatically. The example shows all three approaches.
- Creates an empty `$(TOP)/protocol` directory (e.g. for StreamDevice protocol files).
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type. The `substitutions` structure is defined by the shared `deploy_ioc` schema.
