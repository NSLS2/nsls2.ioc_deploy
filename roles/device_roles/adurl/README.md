# adurl

Deploys an areaDetector IOC using the URL driver, which reads images from URLs
(e.g. files or network cameras serving images over HTTP). The IOC is built from
[ADURL](https://github.com/areaDetector/ADURL) (version `1c725ed`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
adurl-01:
  type: adurl
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{ADURL:01}
```

## Settings

| Setting                | Required | Default | Description                                                    |
| ---------------------- | -------- | ------- | -------------------------------------------------------------- |
| `type`                 | Yes      | -       | Must be `adurl`.                                               |
| `environment.ENGINEER` | Yes      | -       | Name/contact of the responsible engineer.                      |
| `environment.PREFIX`   | Yes      | -       | Base PV prefix. Driver records are loaded at `$(PREFIX)cam1:`. |

## Notes

- Calls `URLDriverConfig("$(PORT)", 0, 0)`. The image URL is set at runtime via
  the driver's PVs.
- Loads the areaDetector common plugins plus the ADCompVision (`CV1:`) and
  ADPluginBar (`Bar1:`) plugins, which are built as module dependencies.
  `auto_settings.req` (in `as/req/`) includes `URLDriver_settings.req`,
  `commonPlugin_settings.req`, and these plugins.
- The templates also support an ffmpeg stream plugin (`ffmstream1:`) when
  `environment.FFMSTREAM_PORT` is set, but `FFMSTREAM_PORT` is not declared in
  `schema.yml`.
- Additional environment defaults: `PORT=URL1`, `XSIZE=1920`, `YSIZE=1080`,
  `QSIZE=20`, `NCHANS=2048`, `CBUFFS=500`, `MAX_THREADS=8`, `NELEMENTS=500000`,
  `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db`. Executable is `URLDriverApp` from
  `iocs/urlIOC`.
