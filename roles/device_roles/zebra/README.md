# zebra

Deploys an IOC for a Zebra position-compare / logic box, connected over a serial line exposed via a terminal server (TCP). The IOC is built from [zebra-ioc](https://github.com/NSLS2/zebra-ioc) (version `8e70cda`). Migrated from the `ioc-deploy` repository to meet updated standards.

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
zebra:
  type: "zebra"

  environment:
    SYS: "XF:05IDD-ES:1"
    DEV: "{Dev:Zebra2}"
    HOSTNAME: "xf31id1-lab3-tsrv1.nsls2.bnl.local"
    PORT: 4004

    # PREFIX is used for common IOC PVs
    PREFIX: XF:05IDD-CT{IOC:Zebra2}
    ENGINEER: "C. Engineer"

    # If CONFIG_FILE is specified
    # the IOC will load parameters from this file (optional)
    # Very questionable, but used in some deployments.
    CONFIG_FILE: "/nsls2/data/srx/shared/config/equipment/zebra2/zebra2_latest"

    # Parameters for the substitutions file
    M1: "XF:05IDD-ES:1{nKB:Smpl-Ax:ssx}Mtr"
    M1DIR: "+"
    M2: "XF:05IDD-ES:1{nKB:Smpl-Ax:ssy}Mtr"
    M2DIR: "+"
    M3: "XF:05IDD-ES:1{nKB:Smpl-Ax:ssz}Mtr"
    M3DIR: "+"
    M4: "XF:05IDD-ES:1{nKB:Smpl-Ax:ssx}Mtr"
    M4DIR: "+"
    NELM: 100000
    PREC: 4

  # Encoder resolutions (4 encoders)
  encoder_resolution: [-9.5368e-05, 9.5368e-05, 9.5368e-05, 0]

  substitutions:
    zebra:
      template_macros: "SYS=$(SYS),DEV=$(DEV)"
      templates:
        - filepath: "$(ZEBRA)/db/zebra.template"
          pattern: ["P", "Q", "PORT", "NELM", "EMPTY", "PREC", "M1", "M1DIR", "M2", "M2DIR", "M3", "M3DIR", "M4", "M4DIR"] # yamllint disable-line rule:line-length
          instances:
            - ["$(SYS)", "$(DEV)", "ZEBRA", "$(NELM)", "", "$(PREC)", "$(M1)", "$(M1DIR)", "$(M2)", "$(M2DIR)", "$(M3)", "$(M3DIR)", "$(M4)", "$(M4DIR)"] # yamllint disable-line rule:line-length
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `zebra`. |
| `environment.SYS` | Yes | - | System portion of the device PV prefix (`P` macro). |
| `environment.DEV` | Yes | - | Device portion of the device PV prefix (`Q` macro), e.g. `{Dev:Zebra2}`. |
| `environment.HOSTNAME` | Yes | - | IP address or hostname of the terminal server; connected to as `$(HOSTNAME):$(PORT)`. |
| `environment.PORT` | Yes | - | TCP port on the terminal server for the Zebra's serial line. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster). |
| `environment.CONFIG_FILE` | No | - | If set, after `iocInit` the IOC writes this path to `$(SYS)$(DEV):CONFIG_FILE` and processes `CONFIG_READ` to restore Zebra parameters from the file. |
| `environment.M1` ... `environment.M4` | Yes | - | Motor PVs for encoders 1-4 (`M1`-`M4` macros). |
| `environment.M1DIR` ... `environment.M4DIR` | Yes | - | `+` or `-`; set to `-` if the motor is inverted in the pmac (decode control = 3 instead of 7). |
| `environment.NELM` | Yes | - | Number of elements in the captured data waveforms. |
| `environment.PREC` | Yes | - | Display precision for position compare gate and pulse fields. |
| `environment.EPICS_DB_INCLUDE_PATH` | No | `$(ZEBRA)/db` | EPICS database include path. |
| `encoder_resolution` | Yes | - | List of exactly 4 numbers; written to `$(SYS)$(DEV):M1:MRES` ... `M4:MRES` after `iocInit`. |
| `substitutions.zebra.template_macros` | Yes | - | Must be `SYS=$(SYS),DEV=$(DEV)`; passed as macros to `dbLoadTemplate`. |
| `substitutions.zebra.templates[].filepath` | Yes | - | Must be `$(ZEBRA)/db/zebra.template`. |
| `substitutions.zebra.templates[].pattern` | Yes | - | Macro names: `P`, `Q`, `PORT`, `NELM`, `EMPTY`, `PREC`, `M1`, `M1DIR`, ... `M4`, `M4DIR`. |
| `substitutions.zebra.templates[].instances` | Yes | - | Rows of exactly 14 string values matching `pattern`. `PORT` must be `ZEBRA` (the asyn port created in `base.cmd`); `EMPTY` is an empty macro to satisfy VDCT. `$(VAR)` references are expanded from the environment when generating `db/zebra.substitutions`. |

## Notes

- `base.cmd` creates the asyn IP port `SERIAL_PORT` to `$(HOSTNAME):$(PORT)` and calls `zebraConfig("ZEBRA", "SERIAL_PORT", 100000)`.
- After `iocInit`, `postInit.cmd` optionally restores the config file and encoder resolutions, then processes `M1:SETPOS` ... `M4:SETPOS` to sync encoder positions with the motors.
- `environment.HOSTNAME` overrides the default `HOSTNAME` IOC environment variable (normally the IOC host's short name).
- Loading parameters from `CONFIG_FILE` is described in the schema as "very questionable, but used in some deployments".
