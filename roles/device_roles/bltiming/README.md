# bltiming

Deploys a beamline timing IOC for MRF timing hardware, configured as either an
event generator (EVG) or event receiver (EVR). The IOC is built from
[elauncher](https://github.com/huyong1979/elauncher) (version `21dede8`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
bltiming-01:
  type: "bltiming"
  # Override default ioc_template root path (default /epics/modules/BL-Timing)
  ioc_template_root_path: "/epics/iocs/epics-mrf-master"
  has_rear_transition_board: false
  mode: "EVG" # EVG|EVR
  environment:
    ENGINEER: "R. Rainer"
    CELL: "XF31"
    # IOC Modules
    AC: "#" # Access Control Enabled
    AS: "#" # AutoSave Enabled
    AS0: "#" # AutoSave Enabled
    AS1: "#" # AutoSave Enabled
    ASR: "#"  # AutoSave Enabled
    caputLog: "#" # caputLog Enabled
    dbl: "" # dbl Enabled

    # Network Information
    MAC: "00:0e:b2:00:08:e3"
    IP: "10.69.58.27"
    NET: "LOB1-LAB3"
    PORT: "26"
    LOC: "Controls Lab 03"
    RACK: "DET POOL"

    # Device Presets
    TYPE: "EVG"
    P: "XF:$(CELL)"
    R: "{EVG}"
    D: "EVG"
    PREFIX: "$(P)$(R)"
```

## Settings

| Setting                     | Required | Default | Description                                                                                                                                                                    |
| --------------------------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `type`                      | Yes      | -       | Must be `bltiming`.                                                                                                                                                            |
| `ioc_template_root_path`    | Yes      | -       | Root path of the timing IOC template. Used for the `st.cmd` shebang (`<path>/bin/linux-x86_64/top`) and to load `<path>/commonSt.cmd` and `<path>/commonInitWithAutoSave.cmd`. |
| `mode`                      | Yes      | -       | `EVG` or `EVR`. Sets the `EVG-Mode`/`EVR-Mode` comment macros and `TYPE` in `st.cmd`.                                                                                          |
| `has_rear_transition_board` | Yes      | -       | Whether a rear transition board is installed. Sets `HAS_REAR_TRANSITION_BOARD` (`0`/`1`), which enables/disables the `UO_*`, `UI_*` and `TB_*` outputs/inputs.                 |
| `environment.ENGINEER`      | Yes      | -       | Name/contact of the responsible engineer.                                                                                                                                      |
| `environment.CELL`          | Yes      | -       | Beamline cell/sector prefix (e.g. `XF31`), used in `P`.                                                                                                                        |
| `environment.AC`            | Yes      | -       | Comment-toggle macro for access control (`""` to enable, `#` to comment out).                                                                                                  |
| `environment.AS`            | Yes      | -       | Comment-toggle macro for autosave.                                                                                                                                             |
| `environment.AS0`           | Yes      | -       | Comment-toggle macro for autosave.                                                                                                                                             |
| `environment.AS1`           | Yes      | -       | Comment-toggle macro for autosave.                                                                                                                                             |
| `environment.ASR`           | Yes      | -       | Comment-toggle macro for autosave restore.                                                                                                                                     |
| `environment.caputLog`      | Yes      | -       | Comment-toggle macro for caPutLog.                                                                                                                                             |
| `environment.dbl`           | Yes      | -       | Comment-toggle macro for `dbl` (record list dump).                                                                                                                             |
| `environment.MAC`           | Yes      | -       | MAC address of the timing device.                                                                                                                                              |
| `environment.IP`            | Yes      | -       | IP address of the timing device.                                                                                                                                               |
| `environment.NET`           | Yes      | -       | Network name the device is connected to.                                                                                                                                       |
| `environment.PORT`          | Yes      | -       | Network switch port the device is connected to.                                                                                                                                |
| `environment.LOC`           | Yes      | -       | Physical location of the device.                                                                                                                                               |
| `environment.RACK`          | Yes      | -       | Rack the device is installed in.                                                                                                                                               |
| `environment.TYPE`          | Yes      | -       | Device type (`EVG`/`EVR`). Overridden in `st.cmd` based on `mode`.                                                                                                             |
| `environment.P`             | Yes      | -       | PV prefix, system part (e.g. `XF:$(CELL)`).                                                                                                                                    |
| `environment.R`             | Yes      | -       | PV prefix, device part (e.g. `{EVG}`).                                                                                                                                         |
| `environment.D`             | Yes      | -       | Device name.                                                                                                                                                                   |
| `environment.PREFIX`        | Yes      | -       | Full PV prefix (e.g. `$(P)$(R)`).                                                                                                                                              |

## Notes

- Does not use the standard `st.cmd`. The role generates `epicsEnv.cmd` (loads
  `/epics/common/<hostname>-netsetup.cmd`, calls `errlogInit(20000)`, and sets
  every environment variable via `epicsEnvSet`) and an `st.cmd` that loads it
  and then the template's `commonSt.cmd` and `commonInitWithAutoSave.cmd`.
