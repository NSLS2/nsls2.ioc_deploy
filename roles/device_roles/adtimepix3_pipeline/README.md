# adtimepix3_pipeline

Deploys a Python IOC that runs the Timepix3 data processing pipeline, writing
processed data to a configurable path. The IOC is installed via pixi from
[tpx3_pipeline](https://github.com/MTakahashi-KWH/tpx3_pipeline) (version
`v0.2.0` by default).

## Example Configuration

Taken from
[`examples/adtimepix3_pipeline_01/config.yml`](examples/adtimepix3_pipeline_01/config.yml):

```yaml
adtimepix3_pipeline_01:
  type: "adtimepix3_pipeline"
  python_ioc_git_revision: "v0.2.0"
  python_version: ">=3.14.0"
  environment:
    PREFIX: "XF:11ID1-ES:TPX:PIPE:1:"
    ENGINEER: "Rhys Takahashi"
    DATA_PATH: "/nsls2/data/chx/assets/timepix/fallback"
```

## Settings

| Setting                   | Required | Default                               | Description                                                                                |
| ------------------------- | -------- | ------------------------------------- | ------------------------------------------------------------------------------------------ |
| `type`                    | Yes      | -                                     | Must be `adtimepix3_pipeline`.                                                             |
| `pixi_executable_path`    | No       | `pixi`                                | Path to the pixi executable used to install dependencies and run the IOC.                  |
| `python_ioc_git_revision` | No       | `v0.2.0`                              | Git tag of `tpx3_pipeline` to install (pixi `pypi-dependencies` entry).                    |
| `python_version`          | No       | `>=3.13`                              | Python version constraint written to `pixi.toml`.                                          |
| `environment.PREFIX`      | Yes      | -                                     | PV prefix, passed to the IOC as `--prefix`.                                                |
| `environment.ENGINEER`    | No       | `Rhys Takahashi <mtakahash1@bnl.gov>` | Used as the `authors` entry in the generated `pixi.toml`.                                  |
| `environment.DATA_PATH`   | Yes      | -                                     | Default output directory for pipeline data, passed as `--path`. Can be changed at runtime. |

## Notes

- No EPICS module is compiled; the role uses a custom (non-standard) `st.cmd`.
- The role writes `pixi.toml`, `pixi.lock`, and `tpx3.json` (event
  clustering/conversion config) to the IOC directory, then runs `pixi install`.
- The bundled `pixi.lock` pins `tpx3-pipeline` to commit `6090707`.
- `st.cmd` is a bash script that sets `EPICS_CA_AUTO_ADDR_LIST=NO`,
  `EPICS_CAS_AUTO_BEACON_ADDR_LIST=NO`, and sets
  `EPICS_CA_ADDR_LIST`/`EPICS_CAS_BEACON_ADDR_LIST` to the host's EPICS
  interface broadcast address. It then runs
  `pixi run python -m tpx3_pipeline.ioc --path <DATA_PATH> --prefix <PREFIX>`.
