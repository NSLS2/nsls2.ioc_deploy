# zpsc

Deploys an IOC for a zPSC power supply controller (4 channels), communicating with the controller over TCP (port 3000) using pscdrv. The IOC is built from [zPSC](https://github.com/NSLS2/zPSC.git) (version `4abc489`), with [pscdrv](https://github.com/mdavidsaver/pscdrv) as a dependency.

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
zpsc-01:
  type: zpsc
  environment:
    ENGINEER: Y. Tian
    SYSTEMS: SR:C12-MG
    DEVICE: PS:SKQ
    NUM: "1"
    BLEN: 100000
    PSC1_IP: "10.0.140.201"
    PREFIX: $(SYSTEMS){$(DEVICE)$(NUM)}
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `zpsc`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.SYSTEMS` | Yes | - | System portion of the PV prefix (`P` macro of all databases). |
| `environment.DEVICE` | Yes | - | Device portion of the PV prefix (`DEVICE` macro). |
| `environment.NUM` | Yes | - | Controller number (string); used as the `NO` macro and in the PSC name `PSC$(NUM)`. Device PVs are `$(SYSTEMS){$(DEVICE)$(NUM)}...`. |
| `environment.BLEN` | Yes | - | Buffer length of the snapshot waveforms (`snapshots.db` `BUFLEN`). |
| `environment.PSC1_IP` | Yes | - | IP address or hostname of the PSC; connected to on port 3000. |
| `environment.PREFIX` | Yes | - | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster); typically `$(SYSTEMS){$(DEVICE)$(NUM)}`. |

## Notes

- `base.cmd` temporarily sets `TOP` to the module directory to load databases from its `db/` directory (`bpc.db`, `lstats.db`, `status10hz.db`, `control_glob.db`, 4x `control_chan.db`, `snapshots.db` for USR/FLT/ERR/INJ/EVR on 4 channels, `wfmstats.db`), creates the PSC with `createPSC("PSC$(NUM)", $(PSC1_IP), 3000, 0)`, then restores `TOP` to the IOC directory.
- `postInit.cmd` initializes channel 1-4 digital outputs, DAC setpoints and op modes (and `Chan2:AveMode-SP`) to defaults, and starts one `ch_fsm` sequencer per channel.
