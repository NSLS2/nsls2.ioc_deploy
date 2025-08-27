# RBD9103

Role for deploying the [NSLS2-developed-IOC](https://github.com/NSLS2/RBD9103) instances for [RBD9103 Pico-Ammeters](https://www.rbdinstruments.com/products/picoammeter.html).

The only required inputs are the device's serial number, which can be extracted via:

```bash
dzdo lsusb -vvv
```

and a PV prefix. See the `example.yml` file for an example configuration.

The role will create a udev rule to allow for non-root access to the device by the softioc user, and will create a symlink to it under `/dev/rbd9103_$SERIAL`.
