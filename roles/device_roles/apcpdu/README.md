# apcpdu

Deploys an SNMP-based IOC for monitoring and controlling one or more APC power distribution units (PDUs). The IOC is built from [BaseSNMPIOC](https://github.com/NSLS2/snmp-bnl) (version `6548d01`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
apcpdu-01:
  type: apcpdu

  devices:
    - TYPE: AP7900
      SYS: "XF:31ID1-ES"
      DEV: "{PDU:1}"
      HOST: "lab3-pdu1.nsls2.bnl.local"
    - TYPE: AP7900
      SYS: "XF:31ID1-ES"
      DEV: "{PDU:2}"
      HOST: "10.69.58.151"
  environment:
    ENGINEER: C. Engineer

    # PREFIX used by any common PVs.
    PREFIX: XF:31ID1-ES{APCPDU-IOC:01}
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `apcpdu`. |
| `devices` | Yes | - | List of PDUs served by this IOC. |
| `devices[].TYPE` | Yes | - | PDU model; one of `AP7900`, `AP7930`, `AP8959`. Selects the `$(BASESNMPIOC)/db/<TYPE>.db` database. |
| `devices[].SYS` | Yes | - | System portion of the PDU's PV prefix (`SYS` macro). |
| `devices[].DEV` | Yes | - | Device portion of the PDU's PV prefix (`DEV` macro). |
| `devices[].HOST` | Yes | - | IP address or hostname of the PDU, passed as the `IP` macro for SNMP access. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster). |

## Notes

- Executable is `snmp`; the module build requires the `net-snmp-devel` system package.
- `base.cmd` sets `MIBDIRS` to `+$(BASESNMPIOC)/mibs` plus the system IETF/IANA MIB directories and disables SNMP driver debugging (`SNMP_DRV_DEBUG(0)`).
- `makeAutosaveFilesFromDbInfo()` is enabled; `info_settings.req` and `info_positions.req` are used for autosave.
