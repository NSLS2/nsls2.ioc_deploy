# motorsim

Deploys a simulated motor controller IOC (EPICS motor `motorSim` driver), useful for testing and development without real hardware. The IOC is built from [NSLS2/motorSim-ioc](https://github.com/NSLS2/motorSim-ioc) (version `683afc0`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
mc01:
  type: motorsim
  environment:
    PREFIX: "XF:31ID1-ES{MC:01}"
    ENGINEER: "J. Wlodek"
  substitutions:
    motorSim:
      - filepath: "$(TOP)/db/motorSim.template"
        pattern: ["P", "M", "PORT", "ADDR", "EGU", "DHLM", "DLLM"]
        instances:
          - ["XF:31ID1-ES", "{MC:01-Ax:X}Mtr", "$(PORT)", 0, "mm", 100, -100]
          - ["XF:31ID1-ES", "{MC:01-Ax:Y}Mtr", "$(PORT)", 1, "mm", 100, -100]
          - ["XF:31ID1-ES", "{MC:01-Ax:Z}Mtr", "$(PORT)", 2, "mm", 100, -100]
          - ["XF:31ID1-ES", "{MC:01-Ax:Rot}Mtr", "$(PORT)", 3, "deg", 180, -180]
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `motorsim`. |
| `environment.PREFIX` | Yes | - | IOC PV prefix. |
| `environment.ENGINEER` | No | - | Name/contact info of the responsible engineer, added to the IOC environment. |
| `substitutions.motorSim` | Yes | - | Substitutions for the simulated motor axes. Only the first entry is used to configure the controller. |
| `substitutions.motorSim[].filepath` | Yes | - | Must be `$(TOP)/db/motorSim.template`. |
| `substitutions.motorSim[].pattern` | Yes | - | Macro names, in order: `P`, `M`, `PORT`, `ADDR`, `EGU`, `DHLM`, `DLLM`. |
| `substitutions.motorSim[].instances` | Yes | - | One 7-element row per axis: `P` (PV prefix), `M` (motor record name suffix), `PORT` (asyn port, normally `$(PORT)`), `ADDR` (axis number, 0-based), `EGU` (engineering units), `DHLM`/`DLLM` (dial high/low soft limits). The number of rows sets the number of controller axes. |

## Notes

- The asyn port name defaults to `PORT=MTRSIM1` (set via `deploy_ioc_device_specific_env`).
- `base.cmd` calls `motorSimCreateController("$(PORT)", <number of axes>)` and one `motorSimConfigAxis` per instance. Columns are read by position (`ADDR` = 4th, `DHLM` = 6th, `DLLM` = 7th), and the simulated hardware limits are set to the soft limits ±10 (`device_roles_motorsim_soft_limit_offset`) divided by a resolution of `0.01` (`device_roles_motorsim_default_res`), in steps.
- Installs `db/motorSim.template` (with motor record `MRES` fixed at `.01`) and autosave request files `motorSimAxis_settings.req` and a generated `motorSim_settings.req` covering every axis.
