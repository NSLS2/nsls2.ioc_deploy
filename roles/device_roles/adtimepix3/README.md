# adtimepix3

Deploys an areaDetector IOC for Timepix3 detectors, controlled through the detector's HTTP server (e.g. Serval). The IOC is built from [ADTimePix3](https://github.com/areaDetector/ADTimePix3) (version `2faf970`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
adtimepix3-01:
  type: adtimepix3
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{ADTIMEPIX3:01}
    SERVER_URL: http://localhost:8081
    NUM_CHIPS: 4
    NUM_PS: 3
    XSIZE: 512
    YSIZE: 512
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `adtimepix3`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | Base PV prefix. All driver records are loaded at `$(PREFIX)cam1:`. |
| `environment.SERVER_URL` | Yes | - | URL of the Timepix3 control server, passed to `ADTimePixConfig`. |
| `environment.NUM_CHIPS` | Yes | - | Number of chips; one `Chips.template` instance is loaded per chip (`C=CHIP0`, `CHIP1`, ..., `ADDR=<index>`). |
| `environment.NUM_PS` | Yes | - | Number of power supplies; one `OperatingVoltage.template` instance is loaded per supply (`C=Pwr0`, `Pwr1`, ...). |
| `environment.XSIZE` | Yes | - | Max image width in pixels, used by the areaDetector common plugins. |
| `environment.YSIZE` | Yes | - | Max image height in pixels, used by the areaDetector common plugins. |

## Notes

- Executable is `tpx3App` from `iocs/tpx3IOC`; the module build requires the `curl-devel` system package.
- Also loads the `TimePix3Base`, `ADTimePix3`, `File`, `Server`, `Measurement`, `Dashboard` (stats plugin `Stats5:`) and `MaskBPC` templates. The pixel mask is hard-coded for 4 chips (`NELEMENTS=262144`).
- Loads the areaDetector common plugins; `auto_settings.req` (in `as/req/`) includes `ADTimePix_settings.req` and `commonPlugin_settings.req`. ffmpeg/NDCV/NDBar entries in the template are inactive, since those modules are not dependencies of this IOC.
- Additional environment defaults: `PORT=TPX`, `QSIZE=20`, `NCHANS=2048`, `CBUFFS=500`, `MAX_THREADS=8`, `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db`.
