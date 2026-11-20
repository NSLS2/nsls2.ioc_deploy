# remote_svc_ctrl

Deploys a Python IOC that controls (start/stop/restart) and monitors a service
on a remote host (e.g. a detector control unit) over SSH, run from a Pixi
environment. The IOC is built from
[NSLS2/remote-svc-ctrl](https://github.com/NSLS2/remote-svc-ctrl.git) (branch
`main`, pinned by the bundled `pixi.lock`).

## Example Configuration

Taken from
[`examples/remote-svc-ctrl-01/config.yml`](examples/remote-svc-ctrl-01/config.yml):

```yaml
remote-svc-ctrl-01:
  type: "remote_svc_ctrl"
  service_type: systemd
  environment:
    PREFIX: "XF:31ID1-CT{SVC-XSPD:1}"
    USERNAME: xspadmin
    HOST: "xf31id1-lambda1"
    SERVICE: xspd.service
    ENGINEER: "C. Engineer"
```

## Settings

| Setting                | Required | Default   | Description                                                                                                      |
| ---------------------- | -------- | --------- | ---------------------------------------------------------------------------------------------------------------- |
| `type`                 | Yes      | -         | Must be `remote_svc_ctrl`.                                                                                       |
| `pixi_executable_path` | No       | `pixi`    | Path to the `pixi` executable used to install dependencies and run the IOC.                                      |
| `service_type`         | No       | `systemd` | Service manager on the remote host: `systemd` or `initd`. `initd` adds `--initd --sudo` to the IOC command line. |
| `environment.PREFIX`   | Yes      | -         | IOC PV prefix.                                                                                                   |
| `environment.USERNAME` | Yes      | -         | Username on the remote host; combined with `HOST` as `--host USERNAME@HOST`.                                     |
| `environment.HOST`     | Yes      | -         | Hostname or IP address of the remote host.                                                                       |
| `environment.SERVICE`  | Yes      | -         | Name of the service to control on the remote host, typically ending in `.service`.                               |
| `environment.LOG_FILE` | No       | -         | Log file on the remote host to watch for output (`--log-file`). If not set, the service's journal is used.       |
| `environment.ENGINEER` | No       | -         | Name/contact info of the responsible engineer. Informational only; not used by the generated `st.cmd`.           |

## Notes

- Copies `pixi.toml`, `pixi.lock`, `.gitignore`, and `.gitattributes` from
  `files/` into the IOC directory and runs `pixi install` (Python `>=3.13,<3.14`
  from conda-forge). Pixi must be available on the target host.
- Does not use the standard EPICS `st.cmd`; a bash `st.cmd` is generated that
  exports the `EPICS_CA*`/`EPICS_PVA*` network variables from the host's
  `epics_interface` and runs:

  ```bash
  pixi run remote-svc-ctrl <PREFIX> <SERVICE> --host <USERNAME>@<HOST> --log-lines 30
  ```

- This role does not configure SSH access. Before deploying, the softioc user
  must already be able to SSH to `USERNAME@HOST` non-interactively (e.g. via SSH
  keys). That access should be set up by a previous Ansible job or by hand. For
  `initd` services, `USERNAME` also needs `sudo` rights to manage the service.
