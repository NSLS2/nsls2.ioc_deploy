# lakeshore336

Deploys a StreamDevice IOC for a Lake Shore Model 336 temperature controller, with configurable input channels and control loops, over a TCP/IP or serial connection. It uses the generic BaseStreamDevice IOC, built from [BaseStreamDevice](https://github.com/NSLS2/BaseStreamDevice) (version `093e6cf`), together with the databases and protocol file shipped in this role.

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
lakeshore336-01:
  type: "lakeshore336"
  environment:
    ENGINEER: "C. Engineer"
    PORT: LS336
    P: "XF:31ID1-ES"
    R: "{LS336:1}"
    PREFIX: "$(P)$(R)"
    CT_PREFIX: "XF:31ID1-CT{LS336:1}"
  connections:
    LS336: # Should match port name in environment
      type: "IP"
      # Connection to controller, LS336 uses port 7777
      connection: "127.0.0.1:7777"
      output_eos: "\\r\\n"
      input_eos: "\\r\\n"
  channels:
    - name: "A"
      scan: "1 second"
    - name: "B"
      scan: "1 second"
    - name: "C"
      scan: "1 second"
    - name: "D"
      scan: "1 second"
  loops:
    - name: "1"
      scan: "1 second"
    - name: "2"
      scan: "1 second"
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `lakeshore336`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PORT` | Yes | - | asyn port used by the channel/loop records; must match a key in `connections`. |
| `environment.P` | Yes | - | First part of the PV prefix. |
| `environment.R` | Yes | - | Second part of the PV prefix in `{...}` form, e.g. `{LS336:1}`. Top-level fanout records are `$(P)$(R)FOut*`; channel and loop record prefixes are derived from it (see Notes). |
| `environment.PREFIX` | Yes | - | Device prefix, typically `$(P)$(R)`. Exported to the IOC environment only. |
| `environment.CT_PREFIX` | Yes | - | IOC prefix used for the iocAdmin (iocStats), autosave status and reccaster records. |
| `connections` | Yes | - | Map of asyn port name to connection definition. One asyn port is created per entry; the key should match `environment.PORT`. |
| `connections.<name>.type` | Yes | - | `IP` or `Serial`; selects `drvAsynIPPortConfigure` or `drvAsynSerialPortConfigure`. |
| `connections.<name>.connection` | Yes | - | `host:port` for `IP` (the 336 uses TCP port `7777`), or the device file (e.g. `/dev/ttyS0`) for `Serial`. |
| `connections.<name>.output_eos` | Yes | - | Output terminator, set with `asynOctetSetOutputEos` (e.g. `"\\r\\n"`). |
| `connections.<name>.input_eos` | Yes | - | Input terminator, set with `asynOctetSetInputEos` (e.g. `"\\r\\n"`). |
| `connections.<name>.serial_settings` | No | - | Map of serial port options, each applied with `asynSetOption`. |
| `connections.<name>.serial_settings.baud` | Yes* | - | Baud rate: `1200`, `2400`, `4800`, `9600`, `19200`, `38400`, `57600` or `115200`. |
| `connections.<name>.serial_settings.bits` | Yes* | - | Data bits: `8`, `7`, `6` or `5`. |
| `connections.<name>.serial_settings.parity` | Yes* | - | `none`, `even` or `odd`. |
| `connections.<name>.serial_settings.stop` | Yes* | - | Stop bits: `1` or `2`. |
| `connections.<name>.serial_settings.clocal` | Yes* | - | `Y` or `N`. |
| `connections.<name>.serial_settings.crtscts` | Yes* | - | Hardware (RTS/CTS) flow control: `N` or `Y`. |
| `connections.<name>.serial_settings.ixon` | Yes* | - | Software output flow control: `N` or `Y`. |
| `connections.<name>.serial_settings.ixoff` | Yes* | - | Software input flow control: `N` or `Y`. |
| `connections.<name>.serial_settings.ixany` | Yes* | - | `N` or `Y`. |
| `channels` | Yes | - | List of sensor input channels; one `Lakeshore336_chan.template` instance each. |
| `channels[].name` | Yes | - | Input channel (`A`, `B`, `C`, `D`), passed as the `CHAN` macro to protocol calls. |
| `channels[].scan` | Yes | - | SCAN rate of the channel records, e.g. `1 second`. |
| `loops` | Yes | - | List of control loops/outputs; one `Lakeshore336_loop.template` instance each. |
| `loops[].name` | Yes | - | Loop/output number (e.g. `1`, `2`), passed as the `CHAN` macro. |
| `loops[].scan` | Yes | - | SCAN rate of the loop records. |

\* Required only if `serial_settings` is given.

## Notes

- Copies `files/*.template` to `db/` and `files/Lakeshore336.proto` to `protocol/lakeshore336.proto`, and generates `db/lakeshore336.substitutions`, `db/lakeshore336_chan.substitutions` and `db/lakeshore336_loop.substitutions`, all loaded from `iocBoot/base.cmd`.
- Channel and loop record prefixes are built by replacing `{X}` in `R` with `X-Chan:<name>` / `X-Out:<name>` (e.g. `R: "{LS336:1}"` gives `LS336:1-Chan:A`); the braces are dropped.
- The top-level fanout template supports at most 16 channels + loops combined.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
- Possible issues:
  - The substitution templates reference `environment`, `channels` and `loops` directly instead of `ioc.environment`, `ioc.channels` and `ioc.loops` as other templates do.
  - The databases reference `Lakeshore336.proto`, but the protocol file is installed as lowercase `lakeshore336.proto`.
  - The three `dbLoadTemplate` lines are in `templates/base.cmd.j2` and are appended again by a `blockinfile` task, so they appear twice.
  - `templates/base.cmd.j2` references an undefined `serial_settings` variable for `asynSetOption` (should be `connection.value.serial_settings`).
