# lakeshore331

Deploys an IOC for a Lake Shore Model 331 temperature controller over a TCP/IP
or serial connection. It uses the generic BaseStreamDevice IOC, built from
[BaseStreamDevice](https://github.com/NSLS2/BaseStreamDevice) (version
`093e6cf`), together with a database shipped in this role.

## Example Configuration

Taken from
[`examples/lakeshore331-01/config.yml`](examples/lakeshore331-01/config.yml):

```yaml
lakeshore331-01:
  type: lakeshore331
  environment:
    ENGINEER: C. Engineer
    PORT: LS331
    P: XF:31ID1-ES
    R: "{LS331:1}"
    PREFIX: "$(P)$(R)"
    CT_PREFIX: "XF:31ID1-CT{LS331:1}"
  connections:
    LS331:
      type: "IP"
      connection: "127.0.0.1:8000"
      output_eos: "\\r\\n"
      input_eos: "\\r\\n"
```

## Settings

| Setting                                      | Required | Default | Description                                                                                                                  |
| -------------------------------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `type`                                       | Yes      | -       | Must be `lakeshore331`.                                                                                                      |
| `environment.ENGINEER`                       | Yes      | -       | Name/contact of the responsible engineer.                                                                                    |
| `environment.PORT`                           | Yes      | -       | asyn port used by the records (`PORT` macro); must match a key in `connections`.                                             |
| `environment.P`                              | Yes      | -       | First part of the device PV prefix; records are named `$(P)$(R):<NAME>`.                                                     |
| `environment.R`                              | Yes      | -       | Second part of the device PV prefix, e.g. `{LS331:1}`.                                                                       |
| `environment.PREFIX`                         | Yes      | -       | Device prefix, typically `$(P)$(R)`. Exported to the IOC environment only; record names come from `P`/`R`.                   |
| `environment.CT_PREFIX`                      | Yes      | -       | IOC prefix used for the iocAdmin (iocStats), autosave status and reccaster records.                                          |
| `connections`                                | Yes      | -       | Map of asyn port name to connection definition. One asyn port is created per entry; the key should match `environment.PORT`. |
| `connections.<name>.type`                    | Yes      | -       | `IP` or `Serial`; selects `drvAsynIPPortConfigure` or `drvAsynSerialPortConfigure`.                                          |
| `connections.<name>.connection`              | Yes      | -       | `host:port` for `IP`, or the device file (e.g. `/dev/ttyS0`) for `Serial`.                                                   |
| `connections.<name>.output_eos`              | Yes      | -       | Output terminator, set with `asynOctetSetOutputEos` (e.g. `"\\r\\n"`).                                                       |
| `connections.<name>.input_eos`               | Yes      | -       | Input terminator, set with `asynOctetSetInputEos` (e.g. `"\\r\\n"`).                                                         |
| `connections.<name>.serial_settings`         | No       | -       | Map of serial port options, each applied with `asynSetOption`.                                                               |
| `connections.<name>.serial_settings.baud`    | Yes*     | -       | Baud rate: `1200`, `2400`, `4800`, `9600`, `19200`, `38400`, `57600` or `115200`.                                            |
| `connections.<name>.serial_settings.bits`    | Yes*     | -       | Data bits: `8`, `7`, `6` or `5`.                                                                                             |
| `connections.<name>.serial_settings.parity`  | Yes*     | -       | `none`, `even` or `odd`.                                                                                                     |
| `connections.<name>.serial_settings.stop`    | Yes*     | -       | Stop bits: `1` or `2`.                                                                                                       |
| `connections.<name>.serial_settings.clocal`  | Yes*     | -       | `Y` or `N`.                                                                                                                  |
| `connections.<name>.serial_settings.crtscts` | Yes*     | -       | Hardware (RTS/CTS) flow control: `N` or `Y`.                                                                                 |
| `connections.<name>.serial_settings.ixon`    | Yes*     | -       | Software output flow control: `N` or `Y`.                                                                                    |
| `connections.<name>.serial_settings.ixoff`   | Yes*     | -       | Software input flow control: `N` or `Y`.                                                                                     |
| `connections.<name>.serial_settings.ixany`   | Yes*     | -       | `N` or `Y`.                                                                                                                  |

\* Required only if `serial_settings` is given.

## Notes

- Generates `iocBoot/base.cmd` (asyn port setup plus
  `dbLoadTemplate("$(TOP)/db/lakeshore331.substitutions")`), copies
  `files/Lakeshore331.template` to `db/`, and renders
  `db/lakeshore331.substitutions` with a single `{PORT, P, R}` instance. An
  empty `protocol/` directory is also created.
- The database is based on the one from
  [epics-modules/ip](https://github.com/epics-modules/ip) and uses asyn records
  (not StreamDevice protocols); an `INIT` record re-reads the controller
  settings every second until initialization completes.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
- `templates/base.cmd.j2` references an undefined `serial_settings` variable
  when rendering `asynSetOption` calls (should be
  `connection.value.serial_settings`), so configs using `serial_settings` will
  likely fail to render.
