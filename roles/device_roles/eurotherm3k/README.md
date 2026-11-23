# eurotherm3k

Deploys an IOC for Eurotherm 3000-series (e.g. 3504) temperature controllers,
communicating over Modbus TCP. The IOC is built from
[modbus](https://github.com/NSLS2/modbus) (version `bb9fa05`), with the
Eurotherm database templates supplied by this role.

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
eurotherm3504:
  type: "eurotherm3k"
  environment:
    ENGINEER: "C. Engineer"
    DEVICE_IP: "10.69.58.150"
    PORT: "E3K"
    SYS: "XF:31ID1-ES"
    DEV: "{E3K:01}"
    MODBUS_PREFIX: "EURTHM3K"

  substitutions:
    Eurotherm3K:
      - filepath: "$(TOP)/db/eurothermDis.template"
        pattern: ["SYS", "DEV"]
        instances:
          - [$(SYS), $(DEV)]
      - filepath: "$(TOP)/db/eurothermL1.template"
        pattern: ["SYS", "DEV", "modbus_prefix", "rregu"]
        instances:
          - [$(SYS), $(DEV), "$(MODBUS_PREFIX)", 1]
      - filepath: "$(TOP)/db/eurothermL2.template"
        pattern: ["SYS", "DEV", "modbus_prefix", "rregu"]
        instances:
          - [$(SYS), $(DEV), "$(MODBUS_PREFIX)", 1]
      - filepath: "$(TOP)/db/eurothermProg.template"
        pattern: ["SYS", "DEV", "modbus_prefix"]
        instances:
          - [$(SYS), $(DEV), "$(MODBUS_PREFIX)"]
      - filepath: "$(TOP)/db/eurothermRec.template"
        pattern: ["SYS", "DEV", "modbus_prefix"]
        instances:
          - [$(SYS), $(DEV), "$(MODBUS_PREFIX)"]
    asynRecord:
      - filepath: "$(ASYN)/db/asynRecord.db"
        pattern: ["P", "R", "PORT", "ADDR", "IMAX", "OMAX"]
        instances:
          - [$(SYS), $(DEV), $(PORT), 0, 80, 80]
```

## Settings

| Setting                     | Required | Default    | Description                                                                                                                                                                                                                                |
| --------------------------- | -------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `type`                      | Yes      | -          | Must be `eurotherm3k`.                                                                                                                                                                                                                     |
| `environment.SYS`           | Yes      | -          | System portion of the PV prefix; records are named `$(SYS)$(DEV)...`.                                                                                                                                                                      |
| `environment.DEV`           | Yes      | -          | Device portion of the PV prefix (including braces, e.g. `{E3K:01}`).                                                                                                                                                                       |
| `environment.DEVICE_IP`     | Yes      | -          | IP address or hostname of the controller; connected to on Modbus TCP port 502 (`IP_PORT=$(DEVICE_IP):502`).                                                                                                                                |
| `environment.ENGINEER`      | No       | -          | Name/contact of the responsible engineer.                                                                                                                                                                                                  |
| `environment.PORT`          | No       | `E3K`      | Name of the asyn IP port (`drvAsynIPPortConfigure`), also used by the asyn record.                                                                                                                                                         |
| `environment.MODBUS_PREFIX` | No       | `EURTHM3K` | Prefix for the Modbus driver ports `$(MODBUS_PREFIX)_MASTER_RX` (function 3, read, polled every 1000 ms) and `$(MODBUS_PREFIX)_MASTER_TX` (function 6, write). Must match the `modbus_prefix` macro passed to the templates.               |
| `substitutions`             | No       | -          | Map of substitution file name to a list of `{filepath, pattern, instances}` entries; each is rendered into `db/<name>.substitutions` and loaded with `dbLoadTemplate`. The example loads all five Eurotherm templates plus an asyn record. |

## Notes

- The role copies `eurothermDis.template`, `eurothermL1.template`,
  `eurothermL2.template`, `eurothermProg.template`, and `eurothermRec.template`
  into the IOC's `db/` directory. They are only loaded if referenced in
  `substitutions`, as in the example.
  - `eurothermDis`: `DISABLE` record (aliased per loop) used to disable polling;
    `AUTODISABLE` disables polling automatically on a `LOOP1:PV:RBV` read error.
  - `eurothermL1`/`eurothermL2`: PID, setpoint, ramp rate, autotune, and
    readback records for loops 1 and 2. The `rregu` macro sets the initial
    ramp-rate unit (`LOOP<n>:RR:UNIT`: `0` = C/s, `1` = C/min).
  - `eurothermProg`: setpoint program selection/control. `eurothermRec`: recipe
    selection.
- Derived environment values: `RX_PORT=$(MODBUS_PREFIX)_MASTER_RX`,
  `TX_PORT=$(MODBUS_PREFIX)_MASTER_TX`, `IP_PORT=$(DEVICE_IP):502`,
  `PREFIX=$(SYS)$(DEV)` (used for iocStats, autosave status, and reccaster PVs).
- The controller is addressed as Modbus slave `1`; `disconnectOnReadTimeout` is
  enabled on the IP port.
- After `iocInit`, `$(SYS)$(DEV).TMSK` is set to `0x1` and `$(SYS)$(DEV).TIOM`
  to `0x0`. These are asyn record fields, so they rely on the `asynRecord`
  substitution in the example (`P=$(SYS)`, `R=$(DEV)`).
