# admythen

Deploys an areaDetector IOC for DECTRIS Mythen 1D strip detectors, communicating
over a TCP socket. The IOC is built from
[ADMythen](https://github.com/areaDetector/ADMythen) (version `bcf2947`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
admythen-01:
  type: admythen
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{ADMYTHEN:01}
    MYTHEN_IP: 192.168.0.90
    MYTHEN_IP_PORT: 1031
    XSIZE: 1280 # No Y-size for Mythen
    PORT: MSD1
    IP_PORT: MDS1_IP
```

## Settings

| Setting                      | Required | Default        | Description                                                                                           |
| ---------------------------- | -------- | -------------- | ----------------------------------------------------------------------------------------------------- |
| `type`                       | Yes      | -              | Must be `admythen`.                                                                                   |
| `environment.ENGINEER`       | Yes      | -              | Name/contact of the responsible engineer.                                                             |
| `environment.PREFIX`         | Yes      | -              | Base PV prefix. Detector records are loaded at `$(PREFIX)cam1:`, an asyn record at `$(PREFIX)asyn_1`. |
| `environment.MYTHEN_IP`      | Yes      | `192.168.0.90` | IP address or hostname of the Mythen.                                                                 |
| `environment.MYTHEN_IP_PORT` | Yes      | `1031`         | TCP port of the Mythen.                                                                               |
| `environment.XSIZE`          | Yes      | `1280`         | Number of strips (image width), used by the common plugins.                                           |
| `environment.PORT`           | Yes      | `MSD1`         | asyn port name of the detector driver (passed to `mythenConfig`).                                     |
| `environment.IP_PORT`        | Yes      | -              | Intended name of the asyn IP port; currently unused (see Notes).                                      |
| `environment.QSIZE`          | No       | `20`           | Queue size for areaDetector plugins.                                                                  |
| `environment.YSIZE`          | No       | `1`            | Must be `1`; Mythen has no Y size, kept for compatibility.                                            |
| `environment.NCHANS`         | No       | `1280`         | Number of channels for time-series plugins.                                                           |
| `environment.CBUFFS`         | No       | `100`          | Number of frames in the circular buffer plugin.                                                       |
| `environment.MAX_THREADS`    | No       | `8`            | Maximum number of threads per plugin.                                                                 |
| `environment.NELEMENTS`      | No       | `5000000`      | Number of array elements used by the areaDetector common plugins.                                     |

## Notes

- Generates `iocBoot/base.cmd`, which creates asyn IP port `$(IP_PORT_NAME)` to
  `$(MYTHEN_IP):$(MYTHEN_IP_PORT)` (input EOS `\r\n`, output EOS `\r`), calls
  `mythenConfig`, loads `mythen.template` and an `asynRecord`, followed by the
  ADCore `commonPlugins.cmd`.
- Generates `autosave/req/auto_settings.req` with `ADBase_settings.req`,
  `NDFile_settings.req`, `mythen_settings.req`, `NDPluginBase_settings.req`,
  `NDStdArrays_settings.req` and `commonPlugin_settings.req`.
- Additional environment defaults: `IP_PORT_NAME=MDS1_IP`,
  `ADMYTHEN=/epics/modules/ADMythen`,
  `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db:$(ADMYTHEN)/db`.
- Inconsistencies: `base.cmd` uses `IP_PORT_NAME`, not the schema-required
  `IP_PORT`, so `IP_PORT` has no effect. `auto_settings.req` is not added to
  `deploy_ioc_req_file_list`, so autosave does not restore or monitor it.
