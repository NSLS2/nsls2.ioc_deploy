# hiden_stream

Deploys a caproto-based Python IOC for Hiden Analytical instruments, run from a
Pixi environment. The IOC is built from
[NSLS2/hiden](https://github.com/NSLS2/hiden.git) (version `v0.1.0` by default,
configurable via `hiden_git_revision`).

## Example Configuration

Taken from [`examples/hiden01/config.yml`](examples/hiden01/config.yml):

```yaml
hiden01:
  type: "hiden_stream"
  pixi_executable_path: "pixi"
  hiden_git_revision: "main"
  python_version: "=3.10"
  environment:
    PREFIX: "XF:31ID1-ES{HIDEN:Dev-1}"
    ENGINEER: "C. Engineer"
```

## Settings

| Setting                | Required | Default        | Description                                                                                                                  |
| ---------------------- | -------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `type`                 | Yes      | -              | Must be `hiden_stream`.                                                                                                      |
| `pixi_executable_path` | No       | `pixi`         | Path to the `pixi` executable used to initialize the environment, install dependencies, and run the IOC.                     |
| `hiden_git_revision`   | No       | `v0.1.0`       | Git revision (tag, branch, or commit) of `https://github.com/NSLS2/hiden.git` installed as a PyPI dependency.                |
| `python_version`       | No       | `>=3.10,<3.13` | Python version specifier appended to `python` in `pixi add` (e.g. `=3.10`).                                                  |
| `environment.PREFIX`   | Yes      | -              | IOC PV prefix, passed as `--prefix` to `python -m hiden.cap2`. Curly braces are automatically doubled (escaped) for caproto. |
| `environment.ENGINEER` | No       | -              | Name/contact info of the responsible engineer. Informational only; not used by the generated `st.cmd`.                       |

## Notes

- Does not use the standard EPICS `st.cmd`; a bash `st.cmd` is generated that
  exports `EPICS_CA_*`/`EPICS_CAS_*` network variables (from the host's
  `epics_interface.broadcast`) and runs
  `pixi run python -m hiden.cap2 --list-pvs --prefix=...`.
- On deployment, `pixi init` is run in the IOC directory if no `pixi.toml`
  exists, then Python and the `hiden` git package are added with `pixi add` and
  installed with `pixi install`. Pixi must be available on the target host.
