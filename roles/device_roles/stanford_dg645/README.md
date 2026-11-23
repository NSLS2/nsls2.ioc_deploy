# stanford_dg645

Deploys a StreamDevice-based IOC for the Stanford Research Systems DG645 digital
delay generator, communicating over a TCP socket. The IOC is built from
[BaseStreamIOC](https://github.com/NSLS2/BaseStreamDevice) (version `093e6cf`).

## Example Configuration

Taken from [`examples/dg645/config.yml`](examples/dg645/config.yml):

```yaml
dg645:
  type: "stanford_dg645"
  environment:
    ENGINEER: "A. Haque"
    DEVICE_IP: "192.168.150.10"
    DEVICE_PORT: 5025
    P: "XF:31ID1-ES"
    R: "{Dly:1}"
  substitutions:
    # Substitutions for StanfordDG645
    dg645:
      - filepath: "$(TOP)/db/dg645_outputs.template"
        pattern: ["Sys", "Dev", "CHAN", "PORT", "SCAN"]
        instances:
          - ["XF:31ID1-ES", "{Dly:1-Chan:T0}", "0", "IP1", "1 second"]
          - ["XF:31ID1-ES", "{Dly:1-Chan:AB}", "1", "IP1", "1 second"]
          - ["XF:31ID1-ES", "{Dly:1-Chan:CD}", "2", "IP1", "1 second"]
          - ["XF:31ID1-ES", "{Dly:1-Chan:EF}", "3", "IP1", "1 second"]
          - ["XF:31ID1-ES", "{Dly:1-Chan:GH}", "4", "IP1", "1 second"]
      - filepath: "$(TOP)/db/dg645_delay.template"
        pattern: ["Sys", "Dev", "CHAN", "PORT", "SCAN"]
        instances:
          - ["XF:31ID1-ES", "{Dly:1-Chan:T0}", "0", "IP1", "1 second"]
          - ["XF:31ID1-ES", "{Dly:1-Chan:T1}", "1", "IP1", "1 second"]
          - ["XF:31ID1-ES", "{Dly:1-Chan:A}", "2", "IP1", "1 second"]
          - ["XF:31ID1-ES", "{Dly:1-Chan:B}", "3", "IP1", "1 second"]
          - ["XF:31ID1-ES", "{Dly:1-Chan:C}", "4", "IP1", "1 second"]
          - ["XF:31ID1-ES", "{Dly:1-Chan:D}", "5", "IP1", "1 second"]
          - ["XF:31ID1-ES", "{Dly:1-Chan:E}", "6", "IP1", "1 second"]
          - ["XF:31ID1-ES", "{Dly:1-Chan:F}", "7", "IP1", "1 second"]
          - ["XF:31ID1-ES", "{Dly:1-Chan:G}", "8", "IP1", "1 second"]
          - ["XF:31ID1-ES", "{Dly:1-Chan:H}", "9", "IP1", "1 second"]
      - filepath: "$(TOP)/db/dg645_trigger.template"
        pattern: ["Sys", "Dev", "PORT", "SCAN"]
        instances:
          - ["XF:31ID1-ES", "{Dly:1}", "IP1", "1 second"]
```

## Settings

| Setting                   | Required | Default    | Description                                                                                                                                                                                                                                                                                              |
| ------------------------- | -------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`                    | Yes      | -          | Must be `stanford_dg645`.                                                                                                                                                                                                                                                                                |
| `environment.DEVICE_IP`   | Yes      | -          | IP address or hostname of the DG645.                                                                                                                                                                                                                                                                     |
| `environment.DEVICE_PORT` | Yes      | -          | TCP port of the DG645 (integer, minimum 4000; e.g. `5025`).                                                                                                                                                                                                                                              |
| `environment.P`           | Yes      | -          | PV prefix (system part); combined with `R` to form `PREFIX`.                                                                                                                                                                                                                                             |
| `environment.R`           | Yes      | -          | PV prefix (device part); combined with `P` to form `PREFIX`.                                                                                                                                                                                                                                             |
| `environment.ENGINEER`    | No       | -          | Name of the responsible engineer; exported as an IOC environment variable.                                                                                                                                                                                                                               |
| `environment.PORT`        | No       | `DG645`    | asyn port name created by `drvAsynIPPortConfigure` in `base.cmd`.                                                                                                                                                                                                                                        |
| `environment.PREFIX`      | No       | `$(P)$(R)` | IOC PV prefix, used for iocAdmin/autosave status records.                                                                                                                                                                                                                                                |
| `substitutions`           | No       | -          | Map of substitution file name to a list of `filepath`/`pattern`/`instances` entries; each generates `db/<name>.substitutions`, loaded with `dbLoadTemplate`. Use the role's `dg645_outputs.template`, `dg645_delay.template` and `dg645_trigger.template` (macros `Sys`, `Dev`, `CHAN`, `PORT`, `SCAN`). |

## Notes

- Copies `dg645_outputs.template`, `dg645_delay.template` and
  `dg645_trigger.template` into `db/` and `dg645.proto` into `protocol/`.
- `base.cmd` configures the asyn port as
  `drvAsynIPPortConfigure("$(PORT)", "$(IP):$(IP_PORT)", ...)` with `\r\n`
  input/output terminators. Note that it references `IP` and `IP_PORT` rather
  than `DEVICE_IP`/`DEVICE_PORT`, and the `PORT` macro used in the substitutions
  must match the asyn port name.
- Autosave files are generated automatically (`makeAutosaveFiles`).
