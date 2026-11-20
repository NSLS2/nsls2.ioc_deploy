# admerlin

Deploys an areaDetector IOC for Quantum Detectors Merlin (Medipix) detectors,
communicating with the detector's command and data TCP sockets. The IOC is built
from [ADMerlin](https://github.com/areadetector/ADMerlin) (version `f9b6b1b`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
admerlin-01:
  type: admerlin

  # Configure local port if Merlin is connected directly to the server.
  # Comment out otherwise.
  # admerlin_local_intf_mac: "98:b7:85:01:4a:dd"
  # admerlin_local_intf_ip: "192.168.0.1"

  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{ADMERLIN:01}
    MERLIN_IP: "12.34.56.78"
    # The IP port for the command socket
    COMMAND_IPPORT: 6341
    # The IP port for the data socket
    DATA_IPPORT: 6342
    # The model type for this Medipix detector
    MODEL: 3  # 0=Merlin, 1=MedipixXBPM, 2=UomXBPM, 3=MerlinQuad

    XSIZE: 512
    YSIZE: 512
    NELEM: 262144

    QSIZE: 2048

    # The maximum number of frames buffered in the NDPluginCircularBuff plugin
    CBUFFS: 8192
    NELEMENTS: 10000000000
```

## Settings

| Setting                      | Required | Default   | Description                                                                                                                     |
| ---------------------------- | -------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `type`                       | Yes      | -         | Must be `admerlin`.                                                                                                             |
| `admerlin_local_intf_mac`    | No       | -         | MAC address of the host interface connected directly to the detector. Only used together with `admerlin_local_intf_ip`.         |
| `admerlin_local_intf_ip`     | No       | -         | IP address to assign to that local interface.                                                                                   |
| `environment.ENGINEER`       | Yes      | -         | Name/contact of the responsible engineer.                                                                                       |
| `environment.PREFIX`         | Yes      | -         | Base PV prefix. Detector records are loaded at `$(PREFIX)cam1:`.                                                                |
| `environment.MERLIN_IP`      | Yes      | -         | IP address or hostname of the Merlin detector.                                                                                  |
| `environment.COMMAND_IPPORT` | Yes      | -         | TCP port of the command socket (schema suggests `6341`).                                                                        |
| `environment.DATA_IPPORT`    | Yes      | -         | TCP port of the data socket (schema suggests `6342`).                                                                           |
| `environment.MODEL`          | Yes      | -         | Detector type passed to `merlinDetectorConfig`: `0`=Merlin, `1`=MedipixXBPM, `2`=UomXBPM, `3`=MerlinQuad (schema suggests `3`). |
| `environment.XSIZE`          | Yes      | `512`     | Detector size in X, passed to `merlinDetectorConfig` and used by the common plugins.                                            |
| `environment.YSIZE`          | Yes      | `512`     | Detector size in Y, passed to `merlinDetectorConfig` and used by the common plugins.                                            |
| `environment.NELEM`          | Yes      | -         | Number of pixels (e.g. `XSIZE*YSIZE`); exported but not referenced by this role's templates.                                    |
| `environment.QSIZE`          | Yes      | `20`      | Queue size for areaDetector plugins (schema suggests `2048`).                                                                   |
| `environment.CBUFFS`         | Yes      | `500`     | Maximum number of frames buffered in the NDPluginCircularBuff plugin.                                                           |
| `environment.NELEMENTS`      | Yes      | `5000000` | Number of array elements used by the areaDetector common plugins.                                                               |

## Notes

- Generates `iocBoot/base.cmd`, which creates asyn IP ports `$(COMMAND_PORT)`
  (`MLcmd`, `\n` terminators) and `$(DATA_PORT)` (`MLdata`), calls
  `merlinDetectorConfig` and loads `merlin.template`, followed by the ADCore
  `commonPlugins.cmd`. The autosave directory is named `autosave`; no
  role-specific autosave request file is generated.
- If both `admerlin_local_intf_mac` and `admerlin_local_intf_ip` are set, the
  role configures the matching host interface exactly as described for `adeiger`
  (ifcfg file with netmask `255.255.255.192`, MTU 9000 on >1 Gb/s links,
  NetworkManager restart), refusing to touch the SCIENCE/CAM/INST interfaces.
- Additional environment defaults: `PORT=ML`, `NCHANS=2048`, `MAX_THREADS=8`,
  `ADMERLIN=/epics/modules/ADMerlin`,
  `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db:$(ADMERLIN)/db`,
  `COMMAND_PORT=$(PORT)cmd`, `DATA_PORT=$(PORT)data`.
- Inconsistencies: the local interface task uses
  `templates/ifcfg-interface.sh.j2`, which does not exist in this role; the role
  also tries to copy `files/*.cmd`, but there is no `files/` directory (no-op).
  The schema `default=` values for `COMMAND_IPPORT`, `DATA_IPPORT`, `MODEL` and
  `QSIZE` are not applied, and the example's `NELEMENTS: 10000000000` exceeds a
  32-bit integer.
