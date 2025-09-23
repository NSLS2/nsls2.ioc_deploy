#!/usr/bin/env python3

import argparse
import os
import subprocess
import tempfile
import uuid
from pathlib import Path

import yaml


def main():
    parser = argparse.ArgumentParser(description="Deploy example IOC")
    parser.add_argument("ioc_type", help="Type of IOC to deploy")
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
        default="../ansible-roles-nsls2/deploy_ioc.yml",
        help="Path to deployment playbook",
    )
    args = parser.parse_args()

    role_path = Path(f"roles/device_roles/{args.ioc_type}")
    example_path = role_path / "example.yml"

    if not os.path.exists(role_path):
        raise ValueError(f"Unknown IOC type: {args.ioc_type}")

    with open(example_path) as f:
        example_config = yaml.safe_load(f)
        example_ioc_name = list(example_config.keys())[0]

    temp_path = (
        Path(tempfile.gettempdir())
        / f"{args.ioc_type}_example_{str(uuid.uuid4())[:8]}.yml"
    )

    with open(temp_path, "w") as f:
        extra_vars = {"deploy_ioc_extra_host_config": example_config}
        yaml.safe_dump(extra_vars, f)

    playbook_cmd = [
        "ansible-playbook",
        "--limit",
        args.hostname,
        "-e",
        f"deploy_ioc_target={example_ioc_name}",
        "-e",
        f"@{temp_path}",
    ]
    if args.verbose:
        playbook_cmd.append("-vvv")
    if args.dry_run:
        playbook_cmd.append("--check")
    playbook_cmd.append(args.playbook)
    print("Running command:", " ".join(playbook_cmd))

    try:
        subprocess.run(playbook_cmd)
    finally:
        os.remove(temp_path)


if __name__ == "__main__":
    main()
