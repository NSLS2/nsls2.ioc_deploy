# vtcplc

Deploys a vacuum PLC IOC that communicates with an Allen-Bradley (EtherNet/IP)
vacuum control PLC using the EtherIP driver. The IOC is built from
[vacuum-plc](https://github.com/NSLS2/vacuum-plc) (version `7c69152`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
vtcplc-01:
  type: vtcplc
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{VTCPLC:01}
    PLCADR: "10.69.34.74"
    SYS: "Vactest-FEA:"
    SYSPORT: "vactest"
    Template: "fea-plc.template"
```

## Settings

| Setting                | Required | Default | Description                                                                  |
| ---------------------- | -------- | ------- | ---------------------------------------------------------------------------- |
| `type`                 | Yes      | -       | Must be `vtcplc`.                                                            |
| `environment.ENGINEER` | Yes      | -       | Name/contact of the responsible engineer.                                    |
| `environment.PREFIX`   | Yes      | -       | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster).       |
| `environment.PLCADR`   | Yes      | -       | IP address or hostname of the PLC, passed to `drvEtherIP_define_PLC`.        |
| `environment.SYS`      | Yes      | -       | System PV prefix (`Sys` macro); PLC records are loaded as `$(SYS){PLC}...`.  |
| `environment.SYSPORT`  | Yes      | -       | Base name for the EtherIP PLC definition; the PLC is named `$(SYSPORT)_PLC`. |
| `environment.Template` | Yes      | -       | Database file name under `$(VTCPLC)/db` to load (e.g. `fea-plc.template`).   |

## Notes

- Generates `iocBoot/base.cmd`, which runs `EIP_buffer_limit(492)`,
  `drvEtherIP_init()`, defines the PLC on slot `0`, sets `EIP_verbosity(6)`, and
  loads `$(VTCPLC)/db/$(Template)` with
  `Sys=$(SYS),Dev={PLC},PLC=$(SYSPORT)_PLC`.
- The IOC executable is `vacuum_plc`.
