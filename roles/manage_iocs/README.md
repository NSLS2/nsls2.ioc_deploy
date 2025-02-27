# ManageIOCs Ansible Role

This role is meant to provide similar functionality to the `manage-iocs` command line utility.

## Required Inputs

Variable | Type | Purpose
---------|--------|--------
`manage_iocs_command` | One of `start`, `stop`, `install`, `uninstall`, `enable`, `disable`, `restart` | Action to take.
`manage_iocs_subcommand` | Comma-separated string of IOC names, or `all`. | IOCs to perform the action on, if `all`, then perform action on each of the IOCs configured on the target host.
