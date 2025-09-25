#!/usr/bin/env python3

import argparse
import os
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Install module")
    parser.add_argument("module", help="Type of module to install")
    parser.add_argument("hostname", help="Target hostname")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "-d", "--dry-run", action="store_true", help="Perform a dry run"
    )
    parser.add_argument(
        "-p",
        "--playbook",
        default="../ansible-roles-nsls2/install_epics_module.yml",
        help="Path to deployment playbook",
    )
    args = parser.parse_args()

    if not os.path.exists(Path(f"roles/install_module/vars/{args.module}.yml")):
        raise ValueError(f"Unknown module type: {args.module}")

    playbook_cmd = [
        "ansible-playbook",
        "--limit",
        args.hostname,
        "-e",
        f"install_epics_module_to_build={args.module}",
    ]
    if args.verbose:
        playbook_cmd.append("-vvv")
    if args.dry_run:
        playbook_cmd.append("--check")
    playbook_cmd.append(args.playbook)
    print("Running command:", " ".join(playbook_cmd))

    subprocess.run(playbook_cmd)


if __name__ == "__main__":
    main()
