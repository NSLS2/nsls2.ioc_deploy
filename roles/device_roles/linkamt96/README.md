# linkamt96

Deploys an IOC for a Linkam temperature stage driven by a T96 controller, using
the Linkam SDK. The controller can be connected via a Moxa terminal server
(socat PTY bridge), a local serial port, or USB. The IOC is built from
[linkam3](https://github.com/jwlodek/linkam3) (version `1093365`).

## Example Configuration

Taken from
[`examples/linkamt96-moxa/config.yml`](examples/linkamt96-moxa/config.yml):

```yaml
# Moxa terminal server via socat PTY bridge (recommended).
# Deploys a systemd service that bridges TCP to a local PTY device,
# eliminating the need for the npreal2 kernel module.
linkamt96-moxa:
  type: linkamt96
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{LINKAMT96:01}
    PORT: "LINK3"
    MOXA_HOST: "10.68.42.77"
    MOXA_PORT: "4001"
    LINKAM3_LICENSE_PATH: "/path/to/linkamt96_license.txt"
    LINKAM3_LOG_PATH: "/path/to/linkamt96_log.txt"
```

See also
[`examples/linkamt96-serial/config.yml`](examples/linkamt96-serial/config.yml)
(direct serial, `SERIAL_PORT`) and
[`examples/linkamt96-usb/config.yml`](examples/linkamt96-usb/config.yml) (USB,
`VENDOR_ID`/`PRODUCT_ID`).

## Settings

| Setting                            | Required | Default                  | Description                                                                                                  |
| ---------------------------------- | -------- | ------------------------ | ------------------------------------------------------------------------------------------------------------ |
| `type`                             | Yes      | -                        | Must be `linkamt96`.                                                                                         |
| `environment.ENGINEER`             | Yes      | -                        | Name/contact of the responsible engineer.                                                                    |
| `environment.PREFIX`               | Yes      | -                        | PV prefix for the Linkam records (`$(LINKAM3)/db/Linkam.template`) and IOC admin/autosave records.           |
| `environment.PORT`                 | Yes      | -                        | asyn port name of the Linkam driver.                                                                         |
| `environment.MOXA_HOST`            | No       | -                        | Moxa terminal server IP/hostname. With `MOXA_PORT`, enables the socat PTY bridge connection.                 |
| `environment.MOXA_PORT`            | No       | -                        | Moxa TCP port for the socat PTY bridge (e.g. `4001`).                                                        |
| `environment.SERIAL_PORT`          | No       | -                        | Local serial device (e.g. `/dev/ttyUSB0`), used with `Linkam3ConnectSerial` when no Moxa settings are given. |
| `environment.VENDOR_ID`            | No       | -                        | USB vendor ID, used with `Linkam3ConnectUSB` when neither Moxa nor `SERIAL_PORT` is set.                     |
| `environment.PRODUCT_ID`           | No       | -                        | USB product ID, used with `Linkam3ConnectUSB`.                                                               |
| `environment.LINKAM3_LICENSE_PATH` | No       | `/etc/linkam/Linkam.lsk` | Path to the Linkam SDK license file.                                                                         |
| `environment.LINKAM3_LOG_PATH`     | Yes      | -                        | Path of the Linkam SDK log file; also rotated by the deployed logrotate config.                              |

## Notes

- Connection mode is chosen in this order: Moxa (both `MOXA_HOST` and
  `MOXA_PORT` set), then `SERIAL_PORT`, otherwise USB.
- Moxa mode installs `socat` and deploys/enables a `linkam-pty-<ioc name>`
  systemd service that bridges `TCP:<MOXA_HOST>:<MOXA_PORT>` to
  `/dev/linkam-pty-<ioc name>` (owned by the softioc user/group), replacing the
  npreal2 kernel module. The IOC then connects via `Linkam3ConnectSerial` on
  that PTY. If Moxa settings are later removed, the stale service is stopped,
  disabled and deleted.
- A logrotate config `/etc/logrotate.d/linkam-<ioc name>` is deployed for
  `LINKAM3_LOG_PATH` (100M size, 3 rotations, compressed, `copytruncate`).
- These host-level tasks (`/etc/systemd/system`, `/etc/logrotate.d`, `dnf`)
  require root privileges.
- The startup sleeps 2 s after connecting to display the connection status.
- The module requires the proprietary Linkam SDK and
  `libusb-devel`/`libusbx-devel` packages.
