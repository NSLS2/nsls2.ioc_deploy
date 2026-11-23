# adxspd

Deploys an areaDetector IOC for X-Spectrum Lambda detectors, using the XSPD REST
API. The IOC is built from [ADXSPD](https://github.com/NSLS2/ADXSPD) (version
`986de77`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
adxspd-01:
  type: adxspd
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{XSPD-Det:1}
    XSIZE: 1576
    YSIZE: 1200
    NUM_MODULES: 1
    IP: "192.168.1.1"
    PORT_NUM: 8008
    DEVICE_ID: "lambda01"
```

## Settings

| Setting                   | Required | Default | Description                                                                                                                                  |
| ------------------------- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`                    | Yes      | -       | Must be `adxspd`.                                                                                                                            |
| `environment.ENGINEER`    | Yes      | -       | Name/contact of the responsible engineer.                                                                                                    |
| `environment.PREFIX`      | Yes      | -       | Base PV prefix. Detector records are loaded at `$(PREFIX)cam1:`, per-module records at `$(PREFIX)mod<N>:`.                                   |
| `environment.XSIZE`       | Yes      | -       | Max image width in pixels, used by the areaDetector common plugins.                                                                          |
| `environment.YSIZE`       | Yes      | -       | Max image height in pixels, used by the areaDetector common plugins.                                                                         |
| `environment.NUM_MODULES` | Yes      | -       | Number of detector modules; one `ADXSPDModule.template` instance is loaded per module (`R=mod1:` ... `mod<N>:`, asyn port `$(PORT)_MOD<N>`). |
| `environment.IP`          | Yes      | -       | Hostname or IP address of the XSPD server, passed to `ADXSPDConfig`.                                                                         |
| `environment.PORT_NUM`    | Yes      | -       | TCP port of the XSPD server, passed to `ADXSPDConfig`.                                                                                       |
| `environment.DEVICE_ID`   | No       | -       | XSPD device identifier. If not specified, the first device discovered is used.                                                               |

## Notes

- Executable is `xspdApp` from `iocs/xspdIOC`; the module build requires the
  `curl-devel` system package.
- Loads the areaDetector common plugins plus the ADCompVision (`CV1:`) plugin,
  which is built as a module dependency. `auto_settings.req` (in `as/req/`)
  includes `ADXSPD_settings.req`, `commonPlugin_settings.req`, and
  `NDCV_settings.req`.
- The templates also support an ffmpeg stream plugin when
  `environment.FFMSTREAM_PORT` is set, but it is not in `schema.yml` and
  ffmpegServer is not a module dependency, so it is effectively unused.
- Additional environment defaults: `PORT=XSPD1`, `QSIZE=20`, `NCHANS=2048`,
  `CBUFFS=500`, `MAX_THREADS=8`, `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db`.
