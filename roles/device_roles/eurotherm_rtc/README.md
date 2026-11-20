# eurotherm_rtc

Ansible role for deploying eurotherm_rtc IOC instances.

The `operations` section in an IOC configuration is a map of operation names to
boolean toggles. The Modbus definitions are maintained by the role in
`templates/base.cmd.j2`; set an operation to `false` to omit its Modbus configuration
from the generated IOC startup script.
