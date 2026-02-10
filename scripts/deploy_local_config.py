#!/usr/bin/env python3

import argparse
import importlib.util
import logging
import os
import subprocess

import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import questionary
import yaml

NSLS2NETWORK_PKG_AVAILABLE = importlib.util.find_spec("nsls2network") is not None

# Pixi version pin, used if running in
PIXI_VERSION = "v0.55.0"
PIXI_SHA256 = "cb733205ae1a02986071bcbeff47c60460bfb92d1cd9565d40f4dea5448c86a5"

BASE_CONTAINER_IMAGE = "ghcr.io/nsls2/epics-alma"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nsls2.ioc_deploy")


class EscapeCodes(str, Enum):
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    WHITE_ON_RED = "\033[41;97m"


class ColorFormatter(logging.Formatter):
    """ANSI color formatter for warnings and errors."""

    COLOR_MAP = {
        logging.DEBUG: EscapeCodes.CYAN,  # Cyan
        logging.INFO: EscapeCodes.GREEN,  # Green
        logging.WARNING: EscapeCodes.YELLOW,  # Bright Yellow
        logging.ERROR: EscapeCodes.RED,  # Bright Red
        logging.CRITICAL: EscapeCodes.WHITE_ON_RED,  # White on Red bg
    }
    RESET = EscapeCodes.RESET

    def __init__(self, fmt: str, use_color: bool = True):
        super().__init__(fmt)
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        if self.use_color and record.levelno in self.COLOR_MAP:
            # Temporarily modify the levelname with color codes
            original_levelname = record.levelname
            # Pad to 8 characters (length of "CRITICAL") for consistent alignment
            padded_levelname = original_levelname.ljust(8)
            color = self.COLOR_MAP[record.levelno]
            record.levelname = f"{color.value}{padded_levelname}{self.RESET.value}"
            base = super().format(record)
            # Restore the original levelname
            record.levelname = original_levelname
            return base
        # For non-colored output, still pad for consistency
        original_levelname = record.levelname
        record.levelname = original_levelname.ljust(8)
        base = super().format(record)
        record.levelname = original_levelname
        return base


handler = logging.StreamHandler()
use_color = sys.stderr.isatty()
fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
handler.setFormatter(ColorFormatter(fmt, use_color=use_color))
logger.addHandler(handler)
logger.setLevel(logging.INFO)  # By default, hide debug/info messages
logger.propagate = False


def get_all_examples_for_type(ioc_type: str, role_path: Path) -> dict[str, Path]:
    logger.info(f"Identifying examples for IOC type: {ioc_type}")

    all_example_paths = []
    all_examples: dict[str, Path] = {}
    single_example_path = role_path / "example.yml"
    new_examples_path = role_path / "examples"

    if single_example_path.exists():
        logger.debug(f"Found legacy example at {single_example_path}")
        all_example_paths.append(single_example_path)

    if new_examples_path.exists():
        for example in new_examples_path.iterdir():
            example_config_file = example / "config.yml"
            if example_config_file.exists():
                logger.debug(f"Found new-style example at {example_config_file}")
                all_example_paths.append(example_config_file)

    for example_path in all_example_paths:
        try:
            with open(example_path) as fp:
                example_config = yaml.safe_load(fp)
                example_ioc_name = list(example_config.keys())[0]

            logger.debug(f"Loaded example config for IOC: {example_ioc_name}")
            all_examples[example_ioc_name] = example_path
        except Exception as e:
            logger.warning(f"Failed to load example config: {example_path}, error: {e}")

    return all_examples


def ensure_container_running(container_name: str, el_version: int = 8):
    required_image = f"{BASE_CONTAINER_IMAGE}{el_version}:latest"
    logger.info(
        f"Ensuring container {container_name} with image {required_image} is running"
    )
    try:
        subprocess.run(
            [
                f"{Path(__file__).parent.absolute()}/setup_container.sh",
                container_name,
                str(el_version),
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to ensure container is running: {e}") from e


def install_galaxy_collection(
    name: str, is_req_file: bool = False, force: bool = False
):
    cmd = ["ansible-galaxy", "collection", "install"]
    if is_req_file:
        cmd.extend(["-r", name])
    else:
        cmd.append(name)
    if force:
        cmd.append("--force")

    collections_path = Path(__file__).parent.parent / "collections"
    cmd.extend(["-p", str(collections_path.absolute())])
    try:
        logger.info(f"Installing required ansible-galaxy collection(s): {name}")
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to install galaxy collection {name}: {e}") from e


@dataclass
class DeploymentOptions:
    hostname: str
    configs: dict[str, Path]
    verification_files: dict[str, Path]
    dry_run: bool = False
    verbose: bool = False
    skip_compilation: bool = False
    container: bool = False
    el_version: int = 8


def deploy_configs(options: DeploymentOptions):
    deployment_summary: dict[str, tuple[Path, bool]] = {}

    if options.container:
        ensure_container_running(options.hostname, el_version=options.el_version)

    for ioc_name, path in options.configs.items():
        logger.info(f"Deploying config: {ioc_name} from {path}")

        with open(path) as fp:
            config_data = yaml.safe_load(fp)

        if (
            "deploy_ioc_supported_el_versions" in config_data
            and options.el_version
            not in config_data["deploy_ioc_supported_el_versions"]
        ):
            logger.warning(
                f"Skipping {ioc_name} on el{options.el_version}, unsupported"
            )
            continue

        example_skip_compilation = False

        playbook_cmd = [
            "ansible-playbook",
            "--diff",
        ]
        if options.container:
            if ioc_name in options.verification_files:
                with open(options.verification_files[ioc_name]) as fp:
                    verification_data = yaml.safe_load(fp)
                    if verification_data["skip_compilation"]:
                        logger.info(
                            "Skipping module compilation(s) per verification file"
                        )
                        example_skip_compilation = True

            logger.info("Using a local container for the deployment")
            playbook_cmd.extend(
                [
                    "-i",
                    f"{options.hostname},",
                    "-c",
                    "docker",
                    # Our containers come w/ softioc-tst accounts pre-made.
                    "-e",
                    "beamline_acronym=TST",
                ]
            )
        playbook_cmd.extend(
            [
                "-u",
                "root",
                "--limit",
                options.hostname,
                "-e",
                f"deploy_ioc_target={ioc_name}",
                "-e",
                f"deploy_ioc_local_config_path={path}",
                "-e",
                f"deploy_ioc_nsls2network_available={NSLS2NETWORK_PKG_AVAILABLE}",
            ]
        )
        if options.skip_compilation or (options.container and example_skip_compilation):
            logger.info("Skipping any module compilations")
            playbook_cmd.extend(["-e", "install_module_skip_compilation=true"])
        if options.verbose:
            logger.info("Enabling verbose output")
            playbook_cmd.append("-vvv")
        if options.dry_run:
            logger.info("Performing dry run")
            playbook_cmd.append("--check")

        playbook_cmd.append(
            f"{Path(__file__).parent.absolute() / 'deploy_local_ioc_config.yml'}"
        )

        logger.info(f"Executing command: {' '.join(playbook_cmd)}")

        try:
            subprocess.run(playbook_cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Deployment of {ioc_name} failed; exit code {e.returncode}: {e.cmd}"
            )
            deployment_summary[ioc_name] = (path, False)
            continue

        # Only attempt verification if deployment succeeded and a verification file is configured for this IOC
        # and deployment is running in a container
        if ioc_name in options.verification_files and options.container:
            logger.info(f"Verifying deployment of {ioc_name}")
            try:
                subprocess.run(
                    [
                        "docker",
                        "cp",
                        options.verification_files[ioc_name],
                        f"{options.hostname}:verify.yml",
                    ],
                    check=True,
                )
                subprocess.run(
                    [
                        "docker",
                        "exec",
                        f"{options.hostname}",
                        "pixi",
                        "run",
                        "verification",
                        ioc_name,
                    ],
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                logger.error(
                    f"Verification of {ioc_name} failed with exit code {e.returncode}"
                )
                deployment_summary[ioc_name] = (path, False)
                continue

        deployment_summary[ioc_name] = (path, True)

    overall_success = all(success for _, success in deployment_summary.values())
    return overall_success, deployment_summary


def main():
    parser = argparse.ArgumentParser(
        description="Deploy specified local IOC configuration"
    )

    deployment_target_group = parser.add_mutually_exclusive_group(required=True)
    deployment_target_group.add_argument(
        "-l", "--limit", help="Target hostname onto which to deploy the IOCs"
    )
    deployment_target_group.add_argument(
        "--container",
        action="store_true",
        help="Use a local container for the deployment",
    )
    parser.add_argument(
        "-c",
        "--configs",
        nargs="+",
        help="Path to local IOC configuration files to deploy",
    )
    parser.add_argument("-e", "--examples", nargs="+", help="Which examples to deploy")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "-d", "--dry-run", action="store_true", help="Perform a dry run"
    )
    parser.add_argument(
        "--skip_compilation", action="store_true", help="Skip compilation step"
    )

    example_source_group = parser.add_mutually_exclusive_group()
    example_source_group.add_argument("-t", "--type", help="Type of IOC to deploy")
    example_source_group.add_argument(
        "--all", action="store_true", help="Deploy all available examples"
    )

    # TODO: Enable el10 support.
    parser.add_argument(
        "-m",
        "--matrix",
        nargs="+",
        type=int,
        choices=[8, 9],
        default=[8],
        help="Specify the EL matrix version(s)",
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Enable interactive mode"
    )

    args = parser.parse_args()

    top_path = Path(__file__).parent.parent.absolute()

    # Switch to the top level nsls2.ioc_deploy directory
    os.chdir(top_path)
    logger.debug(
        f"Changed working directory to {top_path}"
    )

    # Add the collections path to the environment so that ansible-galaxy can find our locally installed collection(s)
    os.environ["ANSIBLE_COLLECTIONS_PATH"] = str((top_path / "collections").absolute())

    logger.info("Executing deployment of local IOC configuration...")
    logger.info("Arguments:")
    for arg in vars(args):
        logger.info(f"    {arg}: {getattr(args, arg)}")

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    configs_to_deploy: dict[str, Path] = {}
    verification_files: dict[str, Path] = {}


    logger.info("Installing ansible collection requirements")
    install_galaxy_collection(
        str(Path("collections/requirements.yml").absolute()), is_req_file=True
    )
    install_galaxy_collection(str(top_path), force=True)

    if args.container:
        install_galaxy_collection("community.docker")

    if args.all:
        logger.info("Finding all examples for all IOC types")
        device_roles_path = top_path / "roles/device_roles"
        for device_role_path in device_roles_path.iterdir():
            device_role_examples = get_all_examples_for_type(device_role_path.stem, device_role_path)
            configs_to_deploy.update(device_role_examples)

    elif args.type:
        logger.info(f"Loading all examples for IOC type: {args.type}")
        role_path = (
            top_path / "roles/device_roles" / args.type
        )
        if not role_path.exists():
            raise ValueError(f"Unknown IOC type: {args.type}")

        all_examples = get_all_examples_for_type(args.type, role_path)
        if not args.examples:
            if args.interactive:
                configs_to_deploy.update(
                    {
                        example: all_examples[example]
                        for example in questionary.select(
                            "Select examples to deploy:",
                            choices=list(all_examples.keys()),
                        ).ask()
                    }
                )
            else:
                logger.info(f"No example names provided; deploying all for {args.type}")
                configs_to_deploy.update(all_examples)
        else:
            selected_examples = {
                example: all_examples[example]
                for example in args.examples
                if example in all_examples
            }
            [
                logger.warning(
                    f"'{example}' not found in available examples for type {args.type}"
                )
                for example in args.examples
                if example not in selected_examples
            ]
            logger.info(
                f"Selected examples for {args.type}: {list(selected_examples.keys())}"
            )
            configs_to_deploy.update(selected_examples)

        for ioc_name, example_config in configs_to_deploy.items():
            if (example_config.parent.absolute() / "verify.yml").exists():
                logger.info(
                    f"Found verification file configured for example {ioc_name}"
                )
                verification_files[ioc_name] = (
                    example_config.parent.absolute() / "verify.yml"
                )

    if args.configs:
        logger.info(f"Loading specified config files: {args.configs}")
        for cfg in args.configs:
            try:
                with open(cfg) as fp:
                    config = yaml.safe_load(fp)
                    ioc_name = list(config.keys())[0]
                    if ioc_name in configs_to_deploy:
                        logger.warning(
                            f"'{ioc_name}' already loaded; overwriting with {cfg}"
                        )
                    configs_to_deploy[ioc_name] = Path(cfg)
            except Exception as e:
                logger.warning(f"Failed to load config '{cfg}': {e}")

    running_deployment_summary: dict[int, dict[str, tuple[Path, bool]]] = {}

    overall_success = True
    if args.container:
        logger.info(
            f"Executing {len(configs_to_deploy)} containerized local deployment(s) for EL ver: {args.matrix}"
        )
        for el_version in args.matrix:
            logger.info(f"Executing deployment for EL version: {el_version}")
            el_version_success, deployment_summary = deploy_configs(
                DeploymentOptions(
                    hostname=f"nsls2_ioc_deploy_el{el_version}",
                    configs=configs_to_deploy,
                    verification_files=verification_files,
                    dry_run=args.dry_run,
                    verbose=args.verbose,
                    skip_compilation=args.skip_compilation,
                    container=args.container,
                    el_version=el_version,
                )
            )
            overall_success = overall_success and el_version_success
            running_deployment_summary[el_version] = deployment_summary
    else:
        logger.info(f"Executing {len(configs_to_deploy)} deployment(s) onto {args.limit}")
        overall_success, running_deployment_summary = deploy_configs(
            DeploymentOptions(
                hostname=args.limit,
                configs=configs_to_deploy,
                verification_files=verification_files,
                dry_run=args.dry_run,
                verbose=args.verbose,
                skip_compilation=args.skip_compilation,
                container=args.container,
            )
        )

    print("\n\nDeployment Summary:\n=========================================\n")

    if args.container:
        for el_version, deployment_summary in running_deployment_summary.items():
            print(
                f"EL Version: {el_version}\n-----------------------------------------"
            )
            for ioc_name, (path, success) in deployment_summary.items():
                color = EscapeCodes.GREEN.value if success else EscapeCodes.RED.value
                status_text = "Success" if success else "Failed"
                status_msg = f"{color}{status_text}{EscapeCodes.RESET.value}"
                print(f"  {ioc_name} | {path.absolute()}: {status_msg}")
            print()
    else:
        for ioc_name, (path, success) in running_deployment_summary.items():
            color = EscapeCodes.GREEN.value if success else EscapeCodes.RED.value
            status_text = "Success" if success else "Failed"
            status_msg = f"{color}{status_text}{EscapeCodes.RESET.value}"
            print(f"  {ioc_name} | {path.absolute()}: {status_msg}")

    # Exit with 0 code on success, otherwise 1
    if overall_success:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
