# xspress3

Deploys an areaDetector IOC for a Quantum Detectors Xspress3 multi-channel X-ray fluorescence readout system. The IOC is built from [xspress3](https://github.com/epics-modules/xspress3) (version `5f459a1`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
xspress3-01:
  type: xspress3
  environment:
    ENGINEER: C. Engineer
    PREFIX: "XF:31ID1-ES{XSP3:01}:"
    NUM_CHANNELS: 8
    NUM_CARDS: 4
    XSPRESS3_IP: "192.168.0.1"
    CALIBRATION_DIR: "/etc/xspress3/calibration/initial/settings"
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `xspress3`. |
| `simulation` | No | `false` | If `true`, the driver is started in simulation mode (`XS3_SIM=1` passed to `xspress3Config`). |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | Base PV prefix (include trailing `:`). Driver PVs are at `$(PREFIX)det1:`, HDF5 at `$(PREFIX)HDF1:`, processing at `$(PREFIX)Proc1:`; also used for iocStats/autosave status. |
| `environment.NUM_CHANNELS` | Yes | - | Number of detector channels (>= 1). Passed to `xspress3Config`, used to generate per-channel ROI/SCA/MCA plugins and autosave entries, and selects `xspress3Deadtime_<N>Channel.template`. |
| `environment.NUM_CARDS` | Yes | - | Number of Xspress3 cards/systems (>= 1). |
| `environment.XSPRESS3_IP` | Yes | - | Base IP address (or hostname) of the Xspress3 1G/10G interface. Note that this is the IP of the interface on the IOC server side. The IPs of the XS3 cards themselves must be sequential from this base IP (i.e. if `NUM_CARDS` is 4 and `XSPRESS3_IP` is `192.168.0.1`, the cards should have IPs `192.168.0.2` through `192.168.0.5`). |
| `environment.CALIBRATION_DIR` | Yes | - | Calibration/settings directory, written to `$(PREFIX)det1:CONFIG_PATH` before connecting. |
| `environment.PORT` | No | `XSP3` | asyn port name of the Xspress3 driver. |
| `environment.MAX_FRAMES` | No | `16834` | Max frames for the Xspress3 API; also used as `NCHANS` for SCA/ROI-stat time series. |
| `environment.MAX_DRV_FRAMES` | No | `16834` | Max frames for EPICS driver arrays. |
| `environment.NUM_BINS` | No | `4096` | Maximum spectrum size (MCA bins). |
| `environment.QSIZE` | No | `512` | Queue size for areaDetector plugins. |
| `environment.CBUFFS` | No | `8192` | Circular buffer size (set in environment, not referenced by the role's templates). |
| `environment.CIRC_BUFFER` | No | `1` | Enables the driver's circular buffer mode (needed for more than 12216 frames). |
| `environment.EPICS_DB_INCLUDE_PATH` | No | `$(ADCORE)/db:$(XSPRESS3)/db` | EPICS database include path. |

## Notes

- Installs `iocBoot/DefineSCAROI.cmd` and `iocBoot/SetChannelValues.cmd`, which are included once per channel from `base.cmd` (plugin/record setup) and `postInit.cmd` (default PV values) respectively.
- Generates `as/req/auto_settings.req` (ADBase, HDF5, and 48 ROI stats per channel) and monitors it with `P=$(PREFIX)`, in addition to the info-tag based autosave files.
- After `iocInit` the role sets default PVs: `RUN_FLAGS=0`, `NUM_CHANNELS`, `NumImages=16000`, `AcquireTime=0.25`, `CONFIG_PATH=$(CALIBRATION_DIR)` (then waits 2 s), `CONNECT=1`, `CTRL_DTC=Disable`, internal triggering, HDF5 stream mode with zlib compression, and PROC sum filtering.
- `base.cmd` also loads `iocAdminSoft.db` with `IOC=$(IOC_PREFIX)`, but `IOC_PREFIX` is not set by the role or schema.
- `DefineSCAROI.cmd` hardcodes `XSP3` as the source port of the per-channel ROI plugins, so changing `PORT` from the default will break the ROI chain.
