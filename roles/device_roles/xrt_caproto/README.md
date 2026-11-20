# xrt_caproto

Deploys a Python caproto IOC that serves an xrt ray-tracing beamline simulation
defined in an xrt XML project file, run via `caproto.ioc_examples.xrt_xml_ioc`
in a pixi environment. The IOC is built from
[caproto](https://github.com/thopkins32/caproto.git) (version
`e3f8966b177b813f92331553ced85c20288b1712`).

## Example Configuration

Taken from
[`examples/toroid-ioc-01/config.yml`](examples/toroid-ioc-01/config.yml):

```yaml
toroid-ioc-01:
  type: "xrt_caproto"
  pixi_executable_path: "pixi"
  environment:
    PREFIX: "XF:31ID1-ES{SIM:01}"
    ENGINEER: "C. Engineer"
    XML_FILE_NAME: "toroid_focus.xml"
```

## Settings

| Setting                     | Required | Default  | Description                                                                              |
| --------------------------- | -------- | -------- | ---------------------------------------------------------------------------------------- |
| `type`                      | Yes      | -        | Must be `xrt_caproto`.                                                                   |
| `pixi_executable_path`      | No       | `pixi`   | Path to the `pixi` executable used to create the environment and run the IOC.            |
| `python_version`            | No       | `>=3.11` | Python version constraint passed to `pixi add python<version>`.                          |
| `environment.PREFIX`        | Yes      | -        | PV prefix passed to the IOC as `--prefix`.                                               |
| `environment.ENGINEER`      | No       | -        | Name of the responsible engineer.                                                        |
| `environment.XML_FILE_NAME` | Yes      | -        | Name of the xrt XML beamline file, loaded from `db/<XML_FILE_NAME>` (passed as `--xml`). |

## Notes

- Uses a custom `st.cmd` (bash script) instead of the standard EPICS startup
  script; it exports `EPICS_CA_AUTO_ADDR_LIST=NO`,
  `EPICS_CAS_AUTO_BEACON_ADDR_LIST=NO`, and sets
  `EPICS_CA_ADDR_LIST`/`EPICS_CAS_BEACON_ADDR_LIST` to the host's EPICS
  interface broadcast address.
- Initializes a pixi project in the IOC directory (if no `pixi.toml` exists) and
  adds `python`, `numpy`, `h5py`, and the PyPI packages `caproto` (from the git
  commit above) and `xrt>=2.0.0b1`, then verifies the imports.
- The XML file must be supplied to `db/` (e.g. as a manual IOC file alongside
  the config, as in the example's `toroid_focus.xml`); the role does not create
  it.
