# germcaproto

Deploys the caproto-based IOC for the GeRM germanium strip detector from the
`hextools` Python package (`hextools>=0.2.3`, `caproto<1.2.0`), run in a pixi
environment via `python -m hextools.germ.caproto_ioc`.

## Example Configuration

Taken from [`examples/germcaproto/config.yml`](examples/germcaproto/config.yml):

```yaml
germcaproto:
  type: "germcaproto"
  pixi_executable_path: "pixi"
  python_version: "=3.10"
  environment:
    PREFIX: "XF:31ID1-ES{GERMCAPROTO:Dev-1}"
    ENGINEER: "C. Engineer"
```

## Settings

| Setting                | Required | Default        | Description                                                                                       |
| ---------------------- | -------- | -------------- | ------------------------------------------------------------------------------------------------- |
| `type`                 | Yes      | -              | Must be `germcaproto`.                                                                            |
| `pixi_executable_path` | No       | `pixi`         | Path to the `pixi` executable on the target host, used to create the environment and run the IOC. |
| `python_version`       | No       | `>=3.10,<3.13` | Python version specifier appended to `python` in `pixi add` (e.g. `=3.10`).                       |
| `environment.PREFIX`   | Yes      | -              | PV prefix passed to the IOC as `--prefix`. Curly braces are automatically doubled up for caproto. |
| `environment.ENGINEER` | No       | -              | Name/contact of the responsible engineer.                                                         |

## Notes

- Does not use the standard EPICS `st.cmd`; instead a bash `st.cmd` is generated
  that exports `EPICS_CA_AUTO_ADDR_LIST=NO`,
  `EPICS_CAS_AUTO_BEACON_ADDR_LIST=NO`, and sets
  `EPICS_CA_ADDR_LIST`/`EPICS_CAS_BEACON_ADDR_LIST` to the host's
  `epics_interface.broadcast` address, then runs the IOC with `--list-pvs`.
- `pixi` must be available on the target host. The role runs `pixi init` (if no
  `pixi.toml` exists), `pixi add` for Python, `hextools` and `caproto` (from
  PyPI), and `pixi install` in the IOC directory.
