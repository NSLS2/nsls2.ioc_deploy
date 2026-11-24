# AGENTS.md — nsls2.ioc_deploy

Guide for contributors and coding agents working in the `nsls2.ioc_deploy`
Ansible collection.

## Repository overview

`nsls2.ioc_deploy` is an Ansible collection that centralizes the deployment
logic for EPICS IOC instances at NSLS-II. It is used together with:

- the `deploy_ioc.yml` playbook in
  [NSLS2/ansible](https://github.com/NSLS2/ansible), which calls these roles,
  and
- [NSLS2/ioc_host_vars](https://github.com/NSLS2/ioc_host_vars), which stores
  the per-host IOC instance configurations.

Target hosts are RHEL/Alma 8 or 9 ("EL8"/"EL9").

## Directory structure

```text
.
├── roles/
│   ├── deploy_ioc/           # Central role run for every IOC deployment
│   │   ├── vars/<type>.yml   # Per-IOC-type overrides (one per device role)
│   │   └── templates/        # Standard st.cmd, epicsEnv.cmd, common.cmd, ...
│   ├── install_module/       # Clones + compiles required EPICS modules
│   │   └── vars/<module>_<short-hash>.yml  # One file per module version
│   ├── manage_iocs/          # manage-iocs / systemd service handling
│   └── device_roles/<type>/  # One role per IOC/device type
├── schemas/                  # yamale schemas used by the tests
├── scripts/
│   ├── deploy_local_config.py  # Local/container test deployments
│   ├── manage_collection.py    # make/update/delete role + module helpers
│   ├── setup_container.sh      # Prepares the EL8/EL9 test container
│   ├── verify_deployment.py    # Runs verify.yml checks inside the container
│   └── pixi.toml / pixi.lock   # Environment installed inside the container
├── tests/                    # pytest: schema/var/README validation
├── collections/requirements.yml  # Galaxy/git collection dependencies
└── .github/workflows/        # Lint, config validation, test deployments
```

## How a deployment works

1. `deploy_ioc` receives an `ioc` dict (from `ioc_host_vars`) whose `type`
   names a device role.
2. `deploy_ioc/tasks/set-facts.yml` loads `roles/deploy_ioc/vars/<type>.yml`.
   This sets things like `deploy_ioc_required_module`, `deploy_ioc_executable`,
   `deploy_ioc_template_root_path`, `deploy_ioc_use_common`,
   `deploy_ioc_device_specific_env` and `deploy_ioc_req_file_list`.
3. If a module is required, `install_module` resolves its dependency tree from
   `roles/install_module/vars/` and compiles the modules under
   `/epics/modules/`.
4. `deploy_ioc` creates the IOC directory (`/epics/iocs/<name>`) and the
   standard startup files (unless `deploy_ioc_standard_st_cmd: false`).
5. `deploy_ioc` then includes `nsls2.ioc_deploy.device_roles.<type>`, which
   installs the device-specific files (usually `iocBoot/base.cmd`, autosave
   `.req` files, databases, udev rules, etc.).

See [roles/deploy_ioc/README.md](roles/deploy_ioc/README.md) and
[roles/install_module/README.md](roles/install_module/README.md) for the full
variable references.

## Environments and tooling

Everything runs through [pixi](https://pixi.sh). Never use bare `pip`/`python`.

- `default` environment: Ansible, pytest, yamale and the helper scripts.
- `dev` environment: `default` plus the lint tools (pre-commit, ruff, pyright,
  codespell, yamllint, zizmor, nodejs). Versions are pinned in
  [pixi.toml](pixi.toml) and must stay in lockstep with the `rev:`/`entry:` pins
  in [.pre-commit-config.yaml](.pre-commit-config.yaml).

Common tasks (`pixi run <task>`):

| Task                                       | Purpose                                 |
| ------------------------------------------ | --------------------------------------- |
| `tests`                                    | Run the pytest suite                    |
| `lint`                                     | Run every pre-commit hook on all files  |
| `lint-files -- <paths>`                    | Run pre-commit hooks on specific files  |
| `deployment --container -t <role> -m 8 9`  | Test-deploy a role's examples           |
| `deploy-all`                               | Test-deploy every example on EL8 + EL9  |
| `make-role` / `make-module`                | Scaffold a new device role / module     |
| `update-module`                            | Bump a module to a new commit           |
| `delete-role` / `delete-module` / `report` | Remove items / show collection status   |

## Linting

The hook set matches NSLS2/ansible: pre-commit-hooks basics, ruff
(check + format), pyright, codespell, markdownlint, yamllint, zizmor,
actionlint, ansible-lint, biome, shellcheck and gitleaks.

```bash
pixi run -e dev pre-commit install   # run hooks on every commit
pixi run lint                        # all files
pixi run lint-files -- path/to/file  # specific files
```

Notes:

- pre-commit only checks files git knows about. Run `lint-files` on new,
  untracked files before committing.
- CI (`.github/workflows/lint.yml`) runs the hooks on **changed files only**,
  with ansible-lint in a separate job that first installs
  `collections/requirements.yml` into `collections/`. Locally, ansible-lint runs
  `--offline` against `collections/ansible_collections` (populated by the first
  `pixi run deployment`).
- Markdown is limited to 80-character lines (MD013), except tables and code
  blocks. Put long commands in fenced code blocks rather than inline code.
- codespell: add real domain terms (EPICS field names, vendor names) to
  [.codespell.ignore](.codespell.ignore) in lowercase. Vendor MIB files are
  skipped. Don't rename typos inside EPICS record/PV names, since clients depend
  on them. Add an ignore entry instead.
- Unrendered `.j2` templates are excluded from shellcheck.
- Pin third-party GitHub Actions to a full commit SHA with a `# vX.Y.Z` comment
  (zizmor enforces this). Pass `${{ ... }}` values into `run:` steps through
  `env:` rather than inline (zizmor template-injection).

## Tests

```bash
pixi run tests
```

The pytest suite validates, among other things:

- every device role has a `README.md` and a `roles/deploy_ioc/vars/<role>.yml`;
- every example config validates against its role's `schema.yml`;
- `roles/deploy_ioc/vars/*.yml` validate against
  `schemas/device_specific_vars.yml`;
- `roles/install_module/vars/*.yml` validate against the install_module schemas
  (valid URLs, git commit hashes, known module dependencies).

## Test deployments

Requires docker (or podman with a docker shim). Example configs are deployed
into `ghcr.io/nsls2/epics-alma{8,9}:latest` containers named
`nsls2_ioc_deploy_el8` / `nsls2_ioc_deploy_el9`.

```bash
pixi run deployment --container -t <role> -m 8 9      # all examples of a role
pixi run deployment --container -t <role> -e <name>   # selected example(s)
pixi run deployment --container -c path/to/config.yml # arbitrary config file
```

Useful flags: `--skip_compilation`, `-d/--dry-run`, `-v/--verbose`,
`--not-reinstall-collections`, `-i/--interactive`.

How it works:

- `scripts/setup_container.sh` starts the container if needed, installs pixi,
  and copies in `verify_deployment.py`. If a container with that name exists but
  is **stopped**, the script refuses to continue. Start it
  (`docker start nsls2_ioc_deploy_el8`) or remove it first.
- The local collection is symlinked into
  `collections/ansible_collections/nsls2/ioc_deploy`, so local edits are picked
  up without reinstalling.
- After a successful deployment, an example's `verify.yml` (if present) is run
  inside the container. See [Example configs](#example-configs-and-verifyyml).
- **Pre-deploy hooks:** if `roles/device_roles/<role>/test_hooks/pre_deploy.sh`
  and/or `pre_deploy.py` exist, they run as root inside the container once per
  role, before that role's first example is deployed. Use them to create things
  real hosts have but the container lacks (e.g. `/etc/udev/rules.d`). They get
  `IOC_DEPLOY_ROLE` and `IOC_DEPLOY_EL_VERSION`, must be idempotent, only run
  with `--container`, are skipped on `--dry-run`, and are excluded from the
  built collection. A failing hook marks that role's examples as failed.
- Any `.template`, `.db`, `.substitutions`, `.cmd`, `.req`, `.xml`, `.json`,
  `.yaml` or `.toml` files next to an example's `config.yml` are passed to the
  deployment as manual IOC files.

CI (`.github/workflows/test-device-roles.yml`) runs container test deployments
on EL8 and EL9 for every device role touched by a PR (including changes to
`roles/deploy_ioc/vars/<role>.yml`).

## Creating a new device role

Start with the scaffolding tool, then fill in the details:

```bash
pixi run make-role     # optionally creates the install_module entry too
```

A complete device role needs:

1. **`roles/deploy_ioc/vars/<role>.yml`**: `deploy_ioc_device_type` (required;
   one of `Motor`, `Camera`, `Detector`, `Sample Environment`, `Electrometer`,
   `Diagnostic`, `Timing`, `Vacuum`, `PLC`, `Power`, `IO`, or `Misc`), required
   module, executable,
   template root path, common/AD-common flags, autosave `.req` list,
   device-specific env defaults, required system packages, and
   `deploy_ioc_supported_el_versions` if the role only works on one EL version.
2. **`roles/device_roles/<role>/schema.yml`**: yamale schema for the `ioc`
   config. `type: enum("<role>")` is required. Mark optional keys
   `required=False` and comment what each key means.
3. **An example config**: prefer `examples/<name>/config.yml` (plus an optional
   `verify.yml`). Legacy roles use a single `example.yml`. The example must
   validate against `schema.yml` and should deploy cleanly in the test
   container.
4. **`tasks/main.yml` and `templates/`**: usually just `iocBoot/base.cmd` and
   any autosave/db files.
5. **`README.md`**: required by the tests. Follow the existing format (see
   [roles/device_roles/adkinetix/README.md](roles/device_roles/adkinetix/README.md)):
   - a short description, with a link to the IOC/module source repo and version
     from `roles/install_module/vars/<module>.yml`;
   - an **Example Configuration** section embedding the example verbatim;
   - a **Settings** table (`Setting | Required | Default | Description`) with
     one row per schema key;
   - **Notes** for host requirements, udev rules, generated files, etc.

Best practices:

- Use FQCNs (`ansible.builtin.template`, ...) and give every task a `name`.
- Write IOC files under `{{ deploy_ioc_ioc_directory }}` owned by
  `{{ host_config.softioc_user }}`/`{{ host_config.softioc_group }}` with
  explicit quoted modes (`"0664"` files, `"0775"` scripts).
- Read user settings from `ioc.environment.*` and document every key in both
  `schema.yml` and the README. Put defaults in `deploy_ioc_device_specific_env`
  (or role `defaults/`), not hard-coded in templates.
- If a custom `st.cmd` shebang or template uses `deploy_ioc_template_root_path`
  or `deploy_ioc_executable`, make sure the vars file sets them, or use the
  same fallback as the standard template:
  `{{ deploy_ioc_template_root_path | default('/usr/lib64/epics') }}` /
  `{{ deploy_ioc_executable | default('softIoc') }}`. Undefined variables are
  the most common cause of failed test deployments.
- Guard host-specific system paths that may not exist (e.g.
  `/etc/udev/rules.d`) with an `ansible.builtin.stat` check, as `rbd9103` and
  `adpicam` do. Pair it with a `test_hooks/pre_deploy.sh` if CI should still
  exercise that path.
- Prefix any role-specific variables/registers with the role name (e.g.
  `adpicam_udev_rules_dir`).
- Keep vendor-supplied files (MIBs, `.proto`, vendor `.template`/`.db`)
  verbatim under `files/`.
- Add a `verify.yml` to each example so CI checks the generated files, not just
  that the playbook ran. Set `skip_compilation: true` only for modules that need
  proprietary SDKs unavailable in CI.

## Example configs and `verify.yml`

`verify.yml` is validated against [schemas/verify.yml](schemas/verify.yml):

```yaml
---
skip_compilation: false   # true = skip module builds (proprietary SDKs)

verification:
  files_must_exist:        # relative to /epics/iocs/<name>, or absolute
    - iocBoot/st.cmd
    - iocBoot/base.cmd
  file_must_contain:
    iocBoot/base.cmd:
      - "dbLoadDatabase"
  file_must_not_contain:   # optional; e.g. unrendered Jinja
    iocBoot/base.cmd:
      - "{{"
  permissions:
    iocBoot/st.cmd: "0775"
```

## Adding or updating an EPICS module

```bash
pixi run make-module     # new module version
pixi run update-module   # move dependents to a new commit
```

- Module files are named `<name>_<short-commit-hash>.yml` in
  `roles/install_module/vars/`. Add a new file for a new version rather than
  editing an existing one, unless the change is non-breaking and tested on
  hardware.
- List only immediate `module_deps`; transitive dependencies are resolved
  automatically.
- Put required OS packages in the module's `pkg_deps` list so `install_module`
  installs them (missing `-devel` packages are a common CI failure).

## General conventions

- Make surgical changes. Don't reformat unrelated files.
- Never commit secrets (gitleaks runs in pre-commit and CI).
- Don't edit `collections/ansible_collections/` (installed dependencies, git
  ignored) or `scripts/.pixi/`.
- After editing Python, run `pixi run lint-files -- <files>` and
  `pixi run tests`. After editing a role, also run its container test
  deployment.
