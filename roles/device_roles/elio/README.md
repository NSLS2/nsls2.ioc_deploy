# elio

Deploys an IOC for Beckhoff EK9000 bus couplers with attached EL-series I/O
terminals (digital/analog inputs and outputs), communicating over Modbus TCP.
The IOC is built from [elio-ioc](https://github.com/NSLS2/elio-ioc) (version
`b6c1512`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
gpio_ex1:
  type: "elio"
  terminals:
    - POS: 1
      MODEL: "EL3068"
    - POS: 2
      MODEL: "EL4008"
    - POS: 3
      MODEL: "EL1808"
    - POS: 4
      MODEL: "EL1808"
    - POS: 5
      MODEL: "EL2808"
    - POS: 6
      MODEL: "EL2808"
    - POS: 7
      MODEL: "EL3068"
    - POS: 8
      MODEL: "EL1124"
    - POS: 9
      MODEL: "EL3008"
      CHAN_SPECIFIC_CONFIG:
        1: {"LINR": "SLOPE", "EGU": "V"}
        2: {"LINR": "SLOPE", "EGU": "mA"}

  # SYS and DEV: used to generate prefix for each device
  # PREFIX: used for IOC-specific PVs
  # HOST may be an IP address or host name
  # EK9K: port name
  environment:
    SYS: "XF:31ID1-ES"
    DEV: "GPIO:1"
    EK9K: EK9K1
    HOST: 10.69.58.101
    PREFIX: "XF:31ID1-CT{IOC:GPIO1}"
    ENGINEER: "H. Xu"    # Your name/contact info
```

## Settings

| Setting                             | Required | Default      | Description                                                                                                                                                                                                                                                                 |
| ----------------------------------- | -------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`                              | Yes      | -            | Must be `elio`.                                                                                                                                                                                                                                                             |
| `terminals`                         | Yes      | -            | List (at least one) of EL terminals attached to the EK9000.                                                                                                                                                                                                                 |
| `terminals[].POS`                   | Yes      | -            | Position (slot, starting at 1) of the terminal on the coupler.                                                                                                                                                                                                              |
| `terminals[].MODEL`                 | Yes      | -            | Terminal model; one of `EL1034`, `EL1124`, `EL1808`, `EL2124`, `EL2798`, `EL2808`, `EL3008`, `EL3068`, `EL3154`, `EL3164`, `EL3214`, `EL3314`, `EL3318`, `EL4008`, `EL4038`, `EL4104`, `EL4134`, `EL9505`. Selects the `<MODEL>.substitutions`/`<MODEL>.template` database. |
| `terminals[].CHAN_SPECIFIC_CONFIG`  | No       | -            | Map of channel number (from 1) to a map of extra record macros (e.g. `{"LINR": "SLOPE", "EGU": "V"}`). If set, each channel is loaded individually from `<MODEL>.template` with these macros; otherwise `<MODEL>.substitutions` is used.                                    |
| `environment.SYS`                   | Yes      | -            | System portion of the PV prefix.                                                                                                                                                                                                                                            |
| `environment.DEV`                   | Yes      | -            | Device portion of the PV prefix; terminal PVs use `{<DEV>_<POS>}`, coupler status PVs use `<SYS>{<DEV>}`.                                                                                                                                                                   |
| `environment.EK9K`                  | Yes      | -            | Name of the EK9000 asyn port.                                                                                                                                                                                                                                               |
| `environment.HOST`                  | Yes      | -            | IP address or hostname of the EK9000; connected to on port 502.                                                                                                                                                                                                             |
| `environment.PREFIX`                | Yes      | -            | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster).                                                                                                                                                                                                      |
| `environment.ENGINEER`              | Yes      | -            | Name/contact of the responsible engineer.                                                                                                                                                                                                                                   |
| `environment.EPICS_DB_INCLUDE_PATH` | No       | `$(ELIO)/db` | EPICS database include path.                                                                                                                                                                                                                                                |

## Notes

- Generates `iocBoot/base.cmd`, which calls `ek9000Configure` with the number of
  terminals, loads `ek9000_status.db`, and calls `ek9000ConfigureTerminal` for
  each terminal.
- With `CHAN_SPECIFIC_CONFIG`, the channel count is taken from the last digit of
  the model name (e.g. `EL3008` has 8 channels).
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
