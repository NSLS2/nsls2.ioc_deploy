# adphantom

Deploys an areaDetector IOC for Phantom high-speed cameras (e.g. Miro, VEO), using TCP control/data sockets and a raw Ethernet data stream. The IOC is built from [ADPhantom](https://github.com/jwlodek/ADPhantom) (version `afefafc`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
ADPhantom:
  type: "adphantom"
  environment:
    PREFIX: "XF:31ID1-ES{VEO:Cam-1}"
    ENGINEER: "J. Wlodek"
    MAC_ADDR: "1423f21fdeb0"
    INTF: "eno5"
    CAMERA_IP: "100.100.214.107"
    NUM_CINES: 16
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `adphantom`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | Base PV prefix. Camera records are loaded at `$(PREFIX)cam1:`, the image plugin at `$(PREFIX)image1:`. |
| `environment.CAMERA_IP` | Yes | - | IP address or hostname of the camera. |
| `environment.NUM_CINES` | Yes | - | Number of cine (recording partition) record sets to load; `phantomCine.template` is loaded for `CINE=1..NUM_CINES`. |
| `environment.MAC_ADDR` | Yes | - | MAC address (no separators, as in the example) passed to `ADPhantomConfig` for the data stream. |
| `environment.INTF` | Yes | - | Name of the host network interface used for the data stream (passed to `ADPhantomConfig`). |
| `environment.XSIZE` | No | `1280` | Max image width in pixels, used by the areaDetector common plugins. |
| `environment.YSIZE` | No | `960` | Max image height in pixels, used by the areaDetector common plugins. |
| `environment.CTRL_PORT` | No | `7115` | TCP port of the camera control socket. |
| `environment.DATA_PORT` | No | `7116` | TCP port of the camera data socket. |
| `environment.PORT` | No | `PH1` | asyn port name of the camera driver. |

## Notes

- Generates `iocBoot/base.cmd`, which creates asyn IP ports `CTRL` and `DATA`, calls `ADPhantomConfig`, loads `phantomCamera.template` and the cine templates, and configures an `Image1` NDStdArrays plugin (`Int16`/`SHORT`, 6000000 elements, hard-coded), followed by the ADCore `commonPlugins.cmd`. The module build installs `libpcap-devel`.
- Copies a static `auto_settings.req` (`ADBase_settings.req`, `NDStdArrays_settings.req`, `commonPlugin_settings.req`) into `as/req`; it is not added to `deploy_ioc_req_file_list`, so autosave does not restore or monitor it.
- Additional environment defaults: `QSIZE=20`, `NCHANS=1280`, `CBUFFS=100`, `MAX_THREADS=8`, `NELEMENTS=5000000`, `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db`.
