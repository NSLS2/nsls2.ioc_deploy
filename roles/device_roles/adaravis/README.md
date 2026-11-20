# adaravis

Deploys an areaDetector IOC for GigE Vision / USB3 Vision (GenICam) cameras using the Aravis library. The IOC is built from [ADAravis](https://github.com/areaDetector/ADAravis) (version `a0aa4d6`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
adaravis-01:
  type: adaravis
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{ADARAVIS:01}
    # For camera name, use `/opt/aravis/bin/arv-tool-0.8` to list all cameras
    # find the one with the IP you assigned to it, and copy the entire entry
    # without the IP.
    CAMERA_NAME: "Allied Vision Technologies-Manta G-040B (E0022660)-50-0503548886"
    ENABLE_CACHING: 1
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `adaravis`. |
| `adaravis_genicam_xml_converters_url` | No | - | Accepted by the schema, but not used by the role (see Notes). |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | Base PV prefix. Camera records are loaded at `$(PREFIX)cam1:`. |
| `environment.CAMERA_NAME` | Yes | - | Aravis camera name (passed to `aravisConfig` and `arv-tool -n`). Use `/opt/aravis/bin/arv-tool-0.8` to list all cameras, find the one with the IP you assigned to it, and copy the entire entry without the IP. |
| `environment.ENABLE_CACHING` | Yes | - | `0` or `1`; enables GenICam feature caching in `aravisConfig`. The schema declares `default=0`, but no default is actually applied, so it must be set. |

## Notes

- Installs the `aravis` RPM on the host.
- At deploy time, the camera must be reachable: `arv-tool` reads `DeviceModelName` from the camera and dumps its GenICam XML to `xml/<model>.xml`. The [genicam-xml-converters](https://github.com/jwlodek/genicam-xml-converters) tools (version `224b03b`, set by `device_roles_adaravis_genicam_xml_converters_url`/`_version` in `defaults/main.yml`) are then cloned temporarily to generate `db/<model>.template` and Phoebus screens in `bob/<model>`. The generated template is loaded at `$(PREFIX)cam1:` alongside `aravisCamera.template`.
- An `auto_settings.req` is generated with `aravisCamera_settings.req`, `commonPlugin_settings.req`, the `cam1:GC_Gamma` and `cam1:GC_GevSCPSPacketSize` PVs, and optional ffmpeg/NDCV/NDBar plugin settings. The autosave directory is named `autosave`.
- Additional environment defaults: `PORT=ARV1`, `QSIZE=20`, `NCHANS=2048`, `CBUFFS=500`, `MAX_THREADS=8`, `NELEMENTS=500000`, `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db:$(ADGENICAM)/db:$(ADARAVIS)/db`.
- Inconsistency: the schema key `adaravis_genicam_xml_converters_url` is never read; the role uses the `device_roles_adaravis_genicam_xml_converters_url` role variable instead.
