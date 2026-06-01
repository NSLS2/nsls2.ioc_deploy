# Updating Existing Roles

## Updating a Module Version

When a new version of an EPICS module is released:

```bash
pixi run update-module
```

This interactive tool:

1. Lets you select the module to update
2. Prompts for the new git commit hash
3. Creates a new vars file with the updated version
4. Automatically updates all `module_deps` references in other modules
5. Updates all `deploy_ioc_required_module` references in device role vars
6. Optionally deletes the old configuration file

### Manual Version Update

If you prefer to do it manually:

1. Create the new module vars file:
   ```yaml
   # roles/install_module/vars/mymodule_newver.yml
   mymodule_newver:
     name: MyModule
     url: https://github.com/org/MyModule
     version: newver
     # ... same config as before
   ```

2. Update the device role vars to reference the new module:
   ```yaml
   # roles/deploy_ioc/vars/mydevice.yml
   deploy_ioc_required_module: mymodule_newver
   ```

3. Update any modules that depend on this one:
   ```yaml
   # roles/install_module/vars/othermodule_xyz.yml
   othermodule_xyz:
     module_deps:
       - mymodule_newver  # was mymodule_oldver
   ```

4. Delete the old vars file (if no longer needed)

!!! warning
    If the new version contains breaking changes (API changes, removed features), you may need to update the device role's `base.cmd.j2` template and schema as well.

## Modifying a Device Role

### Adding New Environment Variables

1. Add the variable to the schema:
   ```yaml
   # roles/device_roles/mydevice/schema.yml
   environment:
     NEW_VAR: str(required=False)  # Use required=False to avoid breaking existing configs
   ```

2. Reference it in your template if needed:
   ```jinja2
   {# templates/base.cmd.j2 #}
   {% if ioc.environment.NEW_VAR is defined %}
   myFunction("{{ ioc.environment.NEW_VAR }}")
   {% endif %}
   ```

3. Update the example if the variable is required

### Changing Default Behavior

Modify `roles/deploy_ioc/vars/<type>.yml` to change defaults for the IOC type. For example, adding a new device-specific environment variable:

```yaml
deploy_ioc_device_specific_env:
  PORT: "MY_PORT"
  NEW_DEFAULT: "some_value"  # Added
```

### Adding Optional Features

Use Jinja2 conditionals in templates to support optional features without breaking existing configurations:

```jinja2
{% if ioc.environment.OPTIONAL_FEATURE is defined %}
# Optional feature configuration
optionalSetup("{{ ioc.environment.OPTIONAL_FEATURE }}")
{% endif %}
```

## Breaking Changes

Breaking changes to schemas require justification and should be handled carefully:

1. **Add with `required=False` first** — Make the new field optional in a first PR
2. **Migrate existing configurations** — Update all known configurations in a second PR
3. **Make required** — Once all configurations are updated, remove `required=False`

If a breaking change is unavoidable:

- Document it clearly in the PR description
- Update all example configurations
- Ensure CI passes with the new schema
- Consider adding a migration note to the CHANGELOG
