# caparoc

Deploys an IOC for CAPAROC electronic circuit breaker modules, communicating over Modbus TCP (port 502). The IOC is built from [caparoc-ioc](https://github.com/NSLS2/caparoc-ioc) (version `c426a13`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
caparoc-01:
  type: "caparoc"

  environment:
    SYS: "XF:31ID1-ES"
    DEV: "{CAPAROC:1}"
    HOST: 10.69.58.102
    CB_ASYNPORT: "CAPAROC1"
    PREFIX: "XF:31ID1-CT{IOC:CAPAROC1}"
    ENGINEER: "Engineer Name"

  operations:
    - PORT_NAME: "${CB_ASYNPORT}_ERR_RST"
      MODBUS_FUNC: 16
      START_ADDR: 272
      MODBUS_LEN: 4
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_ERR_CNT_RST"
      MODBUS_FUNC: 16
      START_ADDR: 288
      MODBUS_LEN: 13
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_MOD_NUM"
      MODBUS_FUNC: 3
      START_ADDR: 8192
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_CHAN_NUM"
      MODBUS_FUNC: 3
      START_ADDR: 8193
      MODBUS_LEN: 4
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_MIN_NOM_I"
      MODBUS_FUNC: 3
      START_ADDR: 8224
      MODBUS_LEN: 13
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_MAX_NOM_I"
      MODBUS_FUNC: 3
      START_ADDR: 8288
      MODBUS_LEN: 13
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_GLB_STS"
      MODBUS_FUNC: 3
      START_ADDR: 24576
      MODBUS_LEN: 1
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_SYS_INP1"
      MODBUS_FUNC: 3
      START_ADDR: 24577
      MODBUS_LEN: 2
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_SYS_INP2"
      MODBUS_FUNC: 3
      START_ADDR: 24581
      MODBUS_LEN: 5
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_CHAN_STS"
      MODBUS_FUNC: 3
      START_ADDR: 24592
      MODBUS_LEN: 13
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_I_LOAD"
      MODBUS_FUNC: 3
      START_ADDR: 24656
      MODBUS_LEN: 13
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_ERR_CNT"
      MODBUS_FUNC: 3
      START_ADDR: 24720
      MODBUS_LEN: 13
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_CTRL_CHAN_STS"
      MODBUS_FUNC: 3
      START_ADDR: 49168
      MODBUS_LEN: 13
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_CTRL_CHAN_CMD"
      MODBUS_FUNC: 16
      START_ADDR: 49168
      MODBUS_LEN: 13
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_NOM_I_RB"
      MODBUS_FUNC: 3
      START_ADDR: 49232
      MODBUS_LEN: 13
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_NOM_I_SP"
      MODBUS_FUNC: 16
      START_ADDR: 49232
      MODBUS_LEN: 13
      DATA_TYPE: "UINT16"
    - PORT_NAME: "${CB_ASYNPORT}_MOD_NAME"
      MODBUS_FUNC: 3
      START_ADDR: 4096
      MODBUS_LEN: 80
      DATA_TYPE: "STRING_HIGH_LOW"
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `caparoc`. |
| `environment.SYS` | Yes | - | System portion of the PV prefix (`Sys` macro of `caparoc_cb.db`). |
| `environment.DEV` | Yes | - | Device portion of the PV prefix (`Dev` macro of `caparoc_cb.db`). |
| `environment.HOST` | Yes | - | IP address or hostname of the CAPAROC device; connected to on port 502. |
| `environment.CB_ASYNPORT` | Yes | - | Name of the asyn IP port for the device; also used as the `ASYNPORT` macro of `caparoc_cb.db`. |
| `environment.PREFIX` | Yes | - | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster). |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.EPICS_DB_INCLUDE_PATH` | No | `$(CAPAROC)/db` | EPICS database include path. |
| `operations` | Yes | - | List (at least one) of Modbus port configurations, each creating a `drvModbusAsynConfigure` port. |
| `operations[].PORT_NAME` | Yes | - | Name of the Modbus asyn port (e.g. `${CB_ASYNPORT}_ERR_RST`). |
| `operations[].MODBUS_FUNC` | Yes | - | Modbus function code (e.g. `3` = read holding registers, `16` = write multiple registers). |
| `operations[].START_ADDR` | Yes | - | Modbus start register address. |
| `operations[].MODBUS_LEN` | Yes | - | Number of Modbus registers to read/write. |
| `operations[].DATA_TYPE` | Yes | - | One of `UINT16`, `INT16`, `UINT32`, `INT32`, `FLOAT32`, `FLOAT64`, `STRING_HIGH_LOW`. |

## Notes

- Generates `iocBoot/base.cmd`, which configures the asyn IP port with a Modbus interpose layer, one Modbus port per `operations` entry (poll period 100 ms), and loads `$(CAPAROC)/db/caparoc_cb.db`.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
