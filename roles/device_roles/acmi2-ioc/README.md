# acmi2-ioc

Ansible role for deploying the ACMI-2 (Accelerator Charge Monitor Interlock) IOC
at NSLS-II. This IOC monitors injected beam charge from the electron gun and
enforces Accelerator Safety Envelope (ASE) limits by disabling the gun on violation.

## Driver

The IOC application depends on the PSC (Portable Streaming Controller) driver
[`pscdrv`](https://github.com/mdavidsaver/pscdrv), which is automatically built
as a module dependency before `acmi2-ioc` is compiled.

## Required Environment Variables

| Variable   | Description                               |
| ---------- | ----------------------------------------- |
| `IOCNAME`  | PV prefix macro (`P` in dbLoadRecords)    |
| `UNIT`     | Unit macro (`NO` in dbLoadRecords)        |
| `PSC_IP`   | IP address or hostname of the PSC device  |
| `PSC_PORT` | TCP port of the PSC device (default 3000) |
