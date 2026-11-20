# adeiger

Deploys an areaDetector IOC for DECTRIS detectors with the SIMPLON API (Eiger, Eiger2, Pilatus4, Selun). The IOC is built from [ADEiger](https://github.com/areadetector/ADEiger) (version `a7b25dc`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
adeiger-01:
  type: adeiger
  # Detector model must be one of the following: eiger1, eiger2, pilatus4, selun
  detector_model: eiger1

  # Configure local port if Eiger is connected directly to the server.
  # Comment out otherwise.
  # adeiger_local_intf_mac: "98:b7:85:01:4a:dd"
  # adeiger_local_intf_ip: "192.168.0.1"

  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{ADEIGER:01}
    DCU_IP: "192.168.100.10"

    XSIZE: 1030
    YSIZE: 1065

    QSIZE: 2048

    # The maximum number of frames buffered in the NDPluginCircularBuff plugin
    CBUFFS: 8192
    NELEMENTS: 1096950
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `adeiger`. |
| `detector_model` | Yes | - | One of `eiger1`, `eiger2`, `pilatus4`, `selun`. Selects the `$(ADEIGER)/db/<detector_model>.template` database. |
| `adeiger_local_intf_mac` | No | - | MAC address of the host interface connected directly to the detector. Only used together with `adeiger_local_intf_ip`. |
| `adeiger_local_intf_ip` | No | - | IP address (or hostname) to assign to that local interface. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | Base PV prefix. Detector records are loaded at `$(PREFIX)cam1:`. |
| `environment.DCU_IP` | Yes | - | IP address or hostname of the detector control unit (passed to `eigerDetectorConfig`). |
| `environment.STREAM_IP` | No | - | Separate IP/hostname for the data stream interface. If set, it is passed to `eigerDetectorConfig` as an extra argument. |
| `environment.XSIZE` | Yes | `1030` | Max image width in pixels, used by the areaDetector common plugins. |
| `environment.YSIZE` | Yes | `1065` | Max image height in pixels, used by the areaDetector common plugins. |
| `environment.QSIZE` | Yes | `20` | Queue size for areaDetector plugins. |
| `environment.CBUFFS` | Yes | `500` | Maximum number of frames buffered in the NDPluginCircularBuff plugin. |
| `environment.NELEMENTS` | Yes | `1096950` | Number of array elements used by the areaDetector common plugins. |

## Notes

- Generates `iocBoot/base.cmd`, which calls `eigerDetectorConfig` and loads the model-specific template, followed by the ADCore `commonPlugins.cmd`. The autosave directory is named `autosave`; no role-specific autosave request file is generated.
- If both `adeiger_local_intf_mac` and `adeiger_local_intf_ip` are set (for a detector connected directly to the server), the role finds the host interface with that MAC, refuses to touch the SCIENCE/CAM/INST interfaces, writes `/etc/sysconfig/network-scripts/ifcfg-<intf>` (netmask `255.255.255.192`, MTU 9000 if the link is faster than 1 Gb/s) and restarts NetworkManager.
- Additional environment defaults: `PORT=EIG`, `NCHANS=2048`, `MAX_THREADS=8`, `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db:$(ADEIGER)/db`. The module build also installs `zeromq-devel`.
- Inconsistency: the local interface task uses `templates/ifcfg-interface.sh.j2`, which does not exist in this role, so that step will fail if the local interface options are used.
