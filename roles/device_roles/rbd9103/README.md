# rbd9103

Role for deploying the [NSLS2-developed-IOC](https://github.com/NSLS2/RBD9103)
(version `a835e1c`) instances for
[RBD9103 Pico-Ammeters](https://www.rbdinstruments.com/products/picoammeter.html),
connected via USB serial.

## Example Configuration

Taken from [`examples/rbd9103-01/config.yml`](examples/rbd9103-01/config.yml):

```yaml
rbd9103-01:
  type: "rbd9103"
  environment:
    PREFIX: "XF:31ID1-ES{RBD9103-AMM:1}"
    ENGINEER: "J. Wlodek"
    SERIAL_NUMBER: "AQ01SDRE"
    PORT: "RBD"
    SERIAL_PORT: "RBD_TTY"
  substitutions:
    rbd9103:
      - filepath: "$(RBD9103)/db/rbd9103.template"
        pattern: ["P", "R", "PORT"]
        instances:
          - ["XF:31ID1-ES", "{RBD9103-AMM:1}", "RBD"]
      - filepath: "$(RBD9103)/db/rbd9103_recording.template"
        pattern: ["P", "R", "PORT"]
        instances:
          - ["XF:31ID1-ES", "{RBD9103-AMM:1}", "RBD"]
      - filepath: "$(ASYN)/db/asynRecord.db"
        pattern: ["P", "R", "PORT", "ADDR", "OMAX", "IMAX"]
        instances:
          - ["XF:31ID1-ES", "{RBD9103-AMM:1}AsynIO", "RBD_TTY", "0", "0", "0"]
```

See also [`examples/rbd9103-02`](examples/rbd9103-02), which omits
`substitutions` and instead provides a manual
[`rbd9103.substitutions`](examples/rbd9103-02/rbd9103.substitutions) file
alongside the config.

## Settings

| Setting                     | Required | Default   | Description                                                                                                                                                                |
| --------------------------- | -------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`                      | Yes      | -         | Must be `rbd9103`.                                                                                                                                                         |
| `environment.PREFIX`        | Yes      | -         | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster).                                                                                                     |
| `environment.SERIAL_NUMBER` | Yes      | -         | USB serial number of the device; used for the udev rule and the device path `/dev/rbd9103_<SERIAL_NUMBER>`.                                                                |
| `environment.ENGINEER`      | No       | -         | Name/contact of the responsible engineer.                                                                                                                                  |
| `environment.PORT`          | No       | `RBD`     | asyn port name of the RBD9103 driver (`RBD9103Config`).                                                                                                                    |
| `environment.SERIAL_PORT`   | No       | `RBD_TTY` | asyn port name of the low-level serial port.                                                                                                                               |
| `substitutions`             | No       | -         | Generic substitutions map (handled by `deploy_ioc`): each key generates `db/<key>.substitutions` from the listed `filepath`/`pattern`/`instances`, loaded in `common.cmd`. |

## Notes

- The serial number can be extracted via:

  ```bash
  dzdo lsusb -vvv
  ```

- The role creates a udev rule
  (`/etc/udev/rules.d/99-rbd9103-<SERIAL_NUMBER>.rules`, only if
  `/etc/udev/rules.d` exists) to allow non-root access to the device by the
  softioc user, and creates a symlink to it under
  `/dev/rbd9103_<SERIAL_NUMBER>`.
- `base.cmd` configures the serial port at 57600 baud, 8N1, with CRLF
  terminators, and instantiates the driver. It does not load any records itself;
  the records (`rbd9103.template`, `rbd9103_recording.template`,
  `asynRecord.db`) must come from `substitutions` or a manual `.substitutions`
  file.
- `PORT`, `SERIAL_PORT` and `substitutions` are used in the examples but not
  listed in `schema.yml`.
