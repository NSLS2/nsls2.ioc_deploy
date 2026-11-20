# iologik

Deploys an EPICS Modbus/TCP IOC for one or more MOXA ioLogik E1200-series remote I/O modules (E1210, E1211, E1212, E1213, E1214, E1240, E1241, E1242, E1260, E1262). The IOC is built from [NSLS2/modbus](https://github.com/NSLS2/modbus) (version `bb9fa05`), using the `modbusApp` executable.

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
iologik:
  type: "iologik"
  devices:
    - model: "E1210"
      ip: "192.168.127.254"
    - model: "E1211"
      ip: "192.168.127.254"
    - model: "E1212"
      ip: "192.168.127.254"
      dio_config: ["DO", "DO", "DO", "DO", "DO", "DO", "DO", "DO"]
    - model: "E1213"
      ip: "192.168.127.254"
      dio_config: ["DO", "DO", "DO", "DO"]
    - model: "E1214"
      ip: "192.168.127.254"
    - model: "E1240"
      ip: "192.168.127.254"
    - model: "E1241"
      ip: "192.168.127.254"
    - model: "E1242"
      ip: "192.168.127.254"
      dio_config: ["DO", "DO", "DO", "DO"]
    - model: "E1260"
      ip: "192.168.127.254"
    - model: "E1262"
      ip: "192.168.127.254"
  environment:
    SYS: "XF:31ID1-ES"         # Base PV prefix
    # Optional device prefix in {} portion of PV prefix.
    # If not set, `IOLOGIK` will be used. If set, {{ DEV }}-IOL will be used.
    # For example, if unset you can get XF:31ID1-ES{IOLOGIK1:E1240}
    # If set, you would get XF:31ID1-ES{MFC1-IOL1:E1240}
    DEV: "MFC1"
    ENGINEER: "C. Engineer"   # Your name/contact info
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `iologik`. |
| `devices` | Yes | - | List of ioLogik modules served by this IOC. Each entry gets its own asyn port (`IOL<n>`, where `n` is the 1-based list index) and substitutions file `db/ioLogik_<n>_<model>.substitutions`. |
| `devices[].model` | Yes | - | Module model: `E1210`, `E1211`, `E1212`, `E1213`, `E1214`, `E1240`, `E1241`, `E1242`, `E1260`, or `E1262`. Determines the Modbus function codes/addresses and the DI/DO/DIO/AI/AO/Relay/RTD/TC records generated (see `vars/main.yml`). |
| `devices[].ip` | Yes | - | IP address or hostname of the module; connected on Modbus/TCP port `502`. |
| `devices[].dio_config` | Yes for `E1212`, `E1213`, `E1242` only | - | Direction of each configurable DIO channel, as a list of `DI`/`DO`. Must have 8 entries for `E1212` and 4 for `E1213`/`E1242`. Determines whether each DIO channel gets input (`-Sts`) or output (`-Cmd`) records and sets the `DIO<n>-Mode` record. |
| `environment.SYS` | Yes | - | Base PV prefix (`P` macro of all records). |
| `environment.DEV` | No | `IOLOGIK` | Device name in the `{}` portion of the PV prefix. If set, records use `{<DEV>-IOL<n>:<model>}`; otherwise `{IOLOGIK<n>:<model>}`. |
| `environment.ENGINEER` | No | - | Name/contact info of the responsible engineer, added to the IOC environment. Not in `schema.yml`. |

## Notes

- `base.cmd` is generated with one `drvAsynIPPortConfigure` + `modbusInterposeConfig` and the model-specific `drvModbusAsynConfigure` calls per device, followed by `dbLoadTemplate` of that device's generated substitutions file.
- Records use the `bi_bit`, `bo_bit`, `ai`, `ao`, `longin`, `longout`, `ai_average`, `statistics`, and `poll_delay` templates from `$(MODBUS)/db`; `dioConfig.template` is installed into the IOC's `db/` directory for DIO mode records.
