# eurotherm_rtc

Deploys an IOC for a Eurotherm EPC3016 temperature controller (RTC), communicating over Modbus TCP. The IOC is built from [eurotherm-rtc-ioc](https://github.com/NSLS2/eurotherm-rtc-ioc.git) (version `43bcabd`), which depends on the `modbus` module.

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
eurotherm_rtc-01:
  type: eurotherm_rtc

  environment:
    SYS: "XF:31ID1-CT"
    DEV: "{RG:A1-RTC:1}"
    HOST: "192.168.111.222"
    EPC_ASYNPORT: "EPC3016"
    PREFIX: "XF:31ID1-CT{IOC:RTC01}"
    ENGINEER: "C. Engineer"

  operations:
    AI_PV: true
    AI_PV_STATUS: true
    IO1_PV_RB: true
    IO1_STATUS: true
    LOOP_SP1: true
    LOOP_SP1_RB: true
    LOOP_CH1_PROP_BAND: true
    LOOP_CH1_PROP_BAND_RB: true
    LOOP_INTEGRAL_TIME: true
    LOOP_INTEGRAL_TIME_RB: true
    LOOP_DERIVATIVE_TIME: true
    LOOP_DERIVATIVE_TIME_RB: true
    AL1_STATUS: true
    AL1_ACK: true
    AL1_TYPE: true
    AL2_STATUS: true
    AL2_ACK: true
    AL2_TYPE: true
    AL3_STATUS: true
    AL3_ACK: true
    AL3_TYPE: true
    AL4_STATUS: true
    AL4_ACK: true
    AL4_TYPE: true
    AL5_STATUS: true
    AL5_ACK: true
    AL5_TYPE: true
    AL6_STATUS: true
    AL6_ACK: true
    AL6_TYPE: true
    INSTRUMENT_MODE: true
    INSTRUMENT_MODE_RB: true
    ACCESS_PASSWORD: true
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `eurotherm_rtc`. |
| `environment.SYS` | Yes | - | System portion of the PV prefix (`Sys` macro of `EPC3016.db`). |
| `environment.DEV` | Yes | - | Device portion of the PV prefix (`Dev` macro of `EPC3016.db`). |
| `environment.HOST` | Yes | - | IP address or hostname of the controller; connected to on Modbus TCP port 502. |
| `environment.EPC_ASYNPORT` | Yes | - | Name of the asyn IP port. Also the prefix of the per-operation Modbus ports (`$(EPC_ASYNPORT)_<OPERATION>`) and the `ASYNPORT` macro of `EPC3016.db`. |
| `environment.PREFIX` | Yes | - | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster). |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.EPICS_DB_INCLUDE_PATH` | No | `$(EUROTHERM_RTC)/db` | EPICS database include path. |
| `operations` | Yes | - | Map (at least one entry) of operation name to boolean. Each `true` entry configures a Modbus port for that register (see below). |
| `operations.AI_PV`, `AI_PV_STATUS`, `IO1_PV_RB`, `IO1_STATUS` | No | `false` | Read process value and analog/IO1 input status. |
| `operations.LOOP_SP1`, `LOOP_CH1_PROP_BAND`, `LOOP_INTEGRAL_TIME`, `LOOP_DERIVATIVE_TIME` (and `*_RB`) | No | `false` | Write (and read back with `_RB`) setpoint 1 and PID parameters. |
| `operations.AL<n>_STATUS`, `AL<n>_ACK`, `AL<n>_TYPE` (`n` = 1-6) | No | `false` | Read alarm status, acknowledge alarm, and read alarm type for alarms 1-6. |
| `operations.INSTRUMENT_MODE`, `INSTRUMENT_MODE_RB` | No | `false` | Write / read back the instrument mode. |
| `operations.ACCESS_PASSWORD` | No | `false` | Write the access password (string, 9 registers). |

## Notes

- The `operations` section in an IOC configuration is a map of operation names to boolean toggles. The Modbus definitions (function code, start address, length, data type) are maintained by the role in `templates/base.cmd.j2`; set an operation to `false` (or omit it) to omit its Modbus configuration from the generated IOC startup script.
- Each enabled operation calls `drvModbusAsynConfigure("$(EPC_ASYNPORT)_<OPERATION>", ...)` with slave address `1`, a 1000 ms poll period, and plc type `EPC3016`. Reads use function 3, writes function 6, and `ACCESS_PASSWORD` uses function 16 with `ZSTRING_HIGH_LOW`; all others are `UINT16`.
- `EPC3016.db` is always loaded with all records, regardless of which operations are enabled.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
