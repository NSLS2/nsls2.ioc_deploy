# thermo_con_hecr

Deploys a Modbus-based IOC for the Thermo-Con HECR chiller, communicating via
Modbus ASCII over a TCP connection (e.g. a terminal server). The IOC is built
from [thermo_con_hecr](https://github.com/NSLS2/thermo-con-hecr-ioc) (version
`b7300bb`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
thermo_con_hecr-01:
  type: "thermo_con_hecr"

  environment:
    SYS: "XF:31ID1-CT"
    DEV: "{Mir:1-Chl:1}"
    HOST: 10.69.58.105:4001
    HECR_ASYNPORT: "tsrv1-p1"
    PREFIX: "XF:31ID1-CT{IOC:Chl01}"
    ENGINEER: "Engineer Name"

  operations:
    - PORT_NAME: "INTERNAL_TEMPERATURE"
      MODBUS_FUNC: 3
      START_ADDR: 64
      MODBUS_LEN: 1
      DATA_TYPE: "INT16"
    - PORT_NAME: "EXTERNAL_TEMPERATURE"
      MODBUS_FUNC: 3
      START_ADDR: 65
      MODBUS_LEN: 1
      DATA_TYPE: "INT16"
    - PORT_NAME: "AVERAGE_TEMPERATURE"
      MODBUS_FUNC: 3
      START_ADDR: 66
      MODBUS_LEN: 1
      DATA_TYPE: "INT16"
    - PORT_NAME: "STATUS_FLAG"
      MODBUS_FUNC: 3
      START_ADDR: 67
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "ALARM_FLAG_1"
      MODBUS_FUNC: 3
      START_ADDR: 68
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "ALARM_FLAG_2"
      MODBUS_FUNC: 3
      START_ADDR: 69
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "OUTPUT_RATIO"
      MODBUS_FUNC: 3
      START_ADDR: 70
      MODBUS_LEN: 1
      DATA_TYPE: "INT16"
    - PORT_NAME: "CONTROL_OPERATION"
      MODBUS_FUNC: 6
      START_ADDR: 80
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "CONTROL_OPERATION_RB"
      MODBUS_FUNC: 3
      START_ADDR: 80
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "TARGET_TEMPERATURE"
      MODBUS_FUNC: 6
      START_ADDR: 81
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "TARGET_TEMPERATURE_RB"
      MODBUS_FUNC: 3
      START_ADDR: 81
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "OFFSET_VALUE"
      MODBUS_FUNC: 6
      START_ADDR: 82
      MODBUS_LEN: 1
      DATA_TYPE: "INT16"
    - PORT_NAME: "OFFSET_VALUE_RB"
      MODBUS_FUNC: 3
      START_ADDR: 82
      MODBUS_LEN: 1
      DATA_TYPE: "INT16"
    - PORT_NAME: "PB_RANGE"
      MODBUS_FUNC: 6
      START_ADDR: 83
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "PB_RANGE_RB"
      MODBUS_FUNC: 3
      START_ADDR: 83
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "I_CONSTANT"
      MODBUS_FUNC: 6
      START_ADDR: 85
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "I_CONSTANT_RB"
      MODBUS_FUNC: 3
      START_ADDR: 85
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "D_CONSTANT"
      MODBUS_FUNC: 6
      START_ADDR: 86
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "D_CONSTANT_RB"
      MODBUS_FUNC: 3
      START_ADDR: 86
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "HEAT_OUTPUT_LIMIT"
      MODBUS_FUNC: 6
      START_ADDR: 87
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "HEAT_OUTPUT_LIMIT_RB"
      MODBUS_FUNC: 3
      START_ADDR: 87
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "COOL_OUTPUT_LIMIT"
      MODBUS_FUNC: 6
      START_ADDR: 88
      MODBUS_LEN: 1
      DATA_TYPE: "INT16"
    - PORT_NAME: "COOL_OUTPUT_LIMIT_RB"
      MODBUS_FUNC: 3
      START_ADDR: 88
      MODBUS_LEN: 1
      DATA_TYPE: "INT16"
```

## Settings

| Setting                             | Required | Default                 | Description                                                                                                             |
| ----------------------------------- | -------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `type`                              | Yes      | -                       | Must be `thermo_con_hecr`.                                                                                              |
| `environment.SYS`                   | Yes      | -                       | System part of the PV prefix (`Sys` macro of `thermo-con-HECR.db`).                                                     |
| `environment.DEV`                   | Yes      | -                       | Device part of the PV prefix (`Dev` macro of `thermo-con-HECR.db`).                                                     |
| `environment.HOST`                  | Yes      | -                       | `<ip>:<port>` of the chiller's TCP endpoint, passed to `drvAsynIPPortConfigure`.                                        |
| `environment.HECR_ASYNPORT`         | Yes      | -                       | Name of the low-level asyn IP port; also the prefix for each Modbus port name and the `ASYNPORT` macro of the database. |
| `environment.PREFIX`                | Yes      | -                       | IOC prefix used for iocAdmin/autosave status records.                                                                   |
| `environment.ENGINEER`              | Yes      | -                       | Name of the responsible engineer.                                                                                       |
| `environment.EPICS_DB_INCLUDE_PATH` | No       | `$(THERMO_CON_HECR)/db` | Database include path.                                                                                                  |
| `operations`                        | Yes      | -                       | List (at least one) of Modbus register blocks; each creates a `drvModbusAsynConfigure` port.                            |
| `operations[].PORT_NAME`            | Yes      | -                       | Suffix of the Modbus asyn port; the full port name is `$(HECR_ASYNPORT)_<PORT_NAME>`.                                   |
| `operations[].MODBUS_FUNC`          | Yes      | -                       | Modbus function code (e.g. `3` read holding registers, `6` write single register).                                      |
| `operations[].START_ADDR`           | Yes      | -                       | Starting Modbus register address.                                                                                       |
| `operations[].MODBUS_LEN`           | Yes      | -                       | Number of registers to access.                                                                                          |
| `operations[].DATA_TYPE`            | Yes      | -                       | Modbus data type: one of `UINT16`, `INT16`, `UINT32`, `INT32`, `FLOAT32`, `FLOAT64`, `STRING_HIGH_LOW`.                 |

## Notes

- `base.cmd` adds a Modbus ASCII interposer
  (`modbusInterposeConfig(..., 2, 2000, 0)`) with `\r\n` terminators, configures
  one Modbus port per `operations` entry (slave address 1, 1000 ms poll), and
  loads `$(THERMO_CON_HECR)/db/thermo-con-HECR.db`. The `PORT_NAME` values must
  match those expected by that database.
- Autosave files are generated automatically (`makeAutosaveFiles`).
