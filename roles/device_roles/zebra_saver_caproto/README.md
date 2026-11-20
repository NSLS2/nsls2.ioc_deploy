# zebra_saver_caproto

Deploys the SRX Zebra saver caproto IOC (`srx_caproto_iocs.zebra.caproto_ioc`),
a Python IOC run in a pixi environment for saving Zebra data. The IOC is built
from [srx-caproto-iocs](https://github.com/NSLS-II-SRX/srx-caproto-iocs.git)
(version `v0.1.0` by default).

## Example Configuration

Taken from
[`examples/zebra-saver-caproto-01/config.yml`](examples/zebra-saver-caproto-01/config.yml):

```yaml
zebra-saver-caproto-01:
  type: "zebra_saver_caproto"
  srx_caproto_iocs_git_revision: "v0.1.0"
  python_version: "=3.12"
  # pixi_executable_path: "pixi"
  environment:
    PREFIX: "XF:09IDA-ES{ZEBRA_SAVER:01}"
    ENGINEER: "C. Engineer"
```

## Settings

| Setting                         | Required | Default        | Description                                                                   |
| ------------------------------- | -------- | -------------- | ----------------------------------------------------------------------------- |
| `type`                          | Yes      | -              | Must be `zebra_saver_caproto`.                                                |
| `pixi_executable_path`          | No       | `pixi`         | Path to the `pixi` executable used to create the environment and run the IOC. |
| `srx_caproto_iocs_git_revision` | No       | `v0.1.0`       | Git tag/branch/commit of `srx-caproto-iocs` to install.                       |
| `python_version`                | No       | `>=3.10,<3.13` | Python version constraint passed to `pixi add python<version>`.               |
| `environment.PREFIX`            | Yes      | -              | PV prefix passed to the IOC as `--prefix`.                                    |
| `environment.ENGINEER`          | No       | -              | Name of the responsible engineer.                                             |

## Notes

- Uses a custom `st.cmd` (bash script) instead of the standard EPICS startup
  script; it exports `EPICS_CA_AUTO_ADDR_LIST=NO`,
  `EPICS_CAS_AUTO_BEACON_ADDR_LIST=NO`, and sets
  `EPICS_CA_ADDR_LIST`/`EPICS_CAS_BEACON_ADDR_LIST` to the host's EPICS
  interface broadcast address.
- Initializes a pixi project in the IOC directory (if no `pixi.toml` exists),
  adds Python and `srx-caproto-iocs` (as a PyPI git dependency), and runs
  `pixi install`.
- Curly braces in `PREFIX` are automatically doubled (`{` → `{{`) in `st.cmd`,
  as required by caproto.
