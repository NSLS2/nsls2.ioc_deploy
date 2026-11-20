# adpilatus

Deploys an areaDetector IOC for DECTRIS Pilatus detectors, communicating with the detector's camserver (DCU) over TCP. The IOC is built from [ADPilatus](https://github.com/areaDetector/ADPilatus) (version `72c7844`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
det-pilatus01:
  type: adpilatus
  ramdisk_path: /ramdisk
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{PILATUS:01}
    PILATUS_DCU_IP: "xf31id1-pilatus1.nsls2.bnl.local"
    XSIZE: 487
    YSIZE: 195
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `adpilatus`. |
| `ramdisk_path` | No | - | Path of the ramdisk on the Pilatus DCU. If set, a directory at the same path is created on the IOC host (owned by the softioc user, mode `02775`) and the DCU's `<PILATUS_DCU_IP>:<ramdisk_path>` export is NFS-mounted there (only if the DCU answers a ping). |
| `environment.ENGINEER` | No | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | Base PV prefix. Camera records are loaded at `$(PREFIX)cam1:`, the camserver asyn record at `$(PREFIX)camserver:AsynIO`. |
| `environment.PILATUS_DCU_IP` | Yes | - | IP address or hostname of the Pilatus DCU. camserver is reached on port `41234`; also used as the NFS server for `ramdisk_path`. |
| `environment.XSIZE` | Yes | `487` | Detector width in pixels, passed to `pilatusDetectorConfig` and used by the areaDetector common plugins. |
| `environment.YSIZE` | Yes | `195` | Detector height in pixels, passed to `pilatusDetectorConfig` and used by the areaDetector common plugins. |

## Notes

- Creates an asyn IP port `camserver` to `$(PILATUS_DCU_IP):41234` (input EOS `\x18`, output EOS `\n`) and calls `pilatusDetectorConfig("$(PORT)", "camserver", $(XSIZE), $(YSIZE), 0, 0)`.
- Loads the areaDetector common plugins, plus the ADCompVision (`CV1:`) and ADPluginBar (`Bar1:`) plugins, which are built as module dependencies. An `auto_settings.req` covering the driver, common plugins and these plugins is generated in `as/req/`.
- The templates also support an ffmpeg stream plugin (`ffmstream1:`) when `environment.FFMSTREAM_PORT` is set, but `FFMSTREAM_PORT` is not declared in `schema.yml`.
- The NFS mount uses options `defaults,noac,lookupcache=none`; the mount is skipped (without failing) if the DCU is unreachable at deploy time.
- Additional environment defaults: `PORT=PIL1`, `QSIZE=20`, `NCHANS=2048`, `CBUFFS=500`, `MAX_THREADS=8`, `NELEMENTS=500000`, `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db`.
