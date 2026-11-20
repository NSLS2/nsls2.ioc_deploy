# axis_caproto

Deploys the caproto-based IOC for AXIS network cameras from the NSLS-II SRX caproto IOC collection, run in a pixi environment via `python -m srx_caproto_iocs.axis.caproto_ioc`. The IOC is built from [srx-caproto-iocs](https://github.com/NSLS-II-SRX/srx-caproto-iocs) (version `v0.1.0`).

## Example Configuration

Taken from [`examples/axis-caproto-01/config.yml`](examples/axis-caproto-01/config.yml):

```yaml
axis-caproto-01:
  type: "axis_caproto"
  pixi_executable_path: "pixi"
  axis_caproto_srx_caproto_iocs_git_revision: "v0.1.0"
  python_version: "=3.10"
  environment:
    PREFIX: "XF:31ID1-ES{AXIS-CAPROTO:01}"
    ENGINEER: "C. Engineer"
    CAMERA_HOST: "127.0.0.1"
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `axis_caproto`. |
| `pixi_executable_path` | No | `pixi` | Path to the `pixi` executable on the target host, used to create the environment and run the IOC. |
| `axis_caproto_srx_caproto_iocs_git_revision` | No | `v0.1.0` | Git revision (tag/branch/commit) of `srx-caproto-iocs` installed into the pixi environment as a PyPI git dependency. |
| `python_version` | No | `>=3.10,<3.13` | Python version specifier appended to `python` in `pixi add` (e.g. `=3.10`). |
| `environment.PREFIX` | Yes | - | PV prefix passed to the IOC as `--prefix`. Curly braces are automatically doubled up for caproto. |
| `environment.ENGINEER` | No | - | Name/contact of the responsible engineer. |
| `environment.CAMERA_HOST` | Yes | - | Hostname or IP address of the AXIS camera. Note: currently not passed to the IOC by the `st.cmd` template. |

## Notes

- Does not use the standard EPICS `st.cmd`; instead a bash `st.cmd` is generated that exports `EPICS_CA_AUTO_ADDR_LIST=NO`, `EPICS_CAS_AUTO_BEACON_ADDR_LIST=NO`, and sets `EPICS_CA_ADDR_LIST`/`EPICS_CAS_BEACON_ADDR_LIST` to the host's `epics_interface.broadcast` address, then runs the IOC with `--list-pvs`.
- `pixi` must be available on the target host. The role runs `pixi init` (if no `pixi.toml` exists), `pixi add` for Python and `srx-caproto-iocs`, and `pixi install` in the IOC directory.
