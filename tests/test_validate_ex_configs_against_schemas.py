import os
import re
from pathlib import Path

import pytest
import yamale
import yaml

DEVICE_ROLES = [
    role
    for role in os.listdir("roles/device_roles")
    if os.path.isdir(os.path.join("roles/device_roles", role))
]


def get_example_configs(device_role: str) -> list[Path]:
    """
    Find all example config files for a device role.

    Supports both:
    - New structure: roles/device_roles/<role>/examples/<name>/config.yml
    - Legacy structure: roles/device_roles/<role>/example.yml
    """
    role_path = Path("roles/device_roles") / device_role
    configs = []

    # Check for new examples/ structure
    examples_dir = role_path / "examples"
    if examples_dir.is_dir():
        for example_dir in examples_dir.iterdir():
            if example_dir.is_dir():
                config_file = example_dir / "config.yml"
                if config_file.exists():
                    configs.append(config_file)

    # Check for legacy example.yml
    legacy_example = role_path / "example.yml"
    if legacy_example.exists():
        configs.append(legacy_example)

    return configs


def get_verify_files(device_role: str) -> list[Path]:
    """Find all verify.yml files for a device role."""
    role_path = Path("roles/device_roles") / device_role
    verify_files = []

    examples_dir = role_path / "examples"
    if examples_dir.is_dir():
        for example_dir in examples_dir.iterdir():
            if example_dir.is_dir():
                verify_file = example_dir / "verify.yml"
                if verify_file.exists():
                    verify_files.append(verify_file)

    return verify_files


class HostnameValidator(yamale.validators.Validator):
    tag = "hostname"

    def _is_valid(self, value):
        if value[-1] == ".":
            # strip exactly one dot from the right, if present
            value = value[:-1]
        if len(value) > 253:
            return False

        labels = value.split(".")

        # the TLD must be not all-numeric
        if re.match(r"[0-9]+$", labels[-1]):
            return False

        allowed = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(label) for label in labels)


class IOCTypeValidator(yamale.validators.Validator):
    tag = "ioc_type"

    def _is_valid(self, value):
        return value in DEVICE_ROLES


pytestmark = pytest.mark.parametrize("device_role", DEVICE_ROLES)


def test_ensure_example_present(device_role):
    configs = get_example_configs(device_role)
    assert len(configs) > 0, (
        f"No example configuration found for {device_role} role. "
        f"Expected examples/<name>/config.yml or example.yml"
    )


def test_ensure_required_schema_present(device_role):
    schema_path = os.path.join("roles/device_roles", device_role, "schema.yml")
    assert os.path.exists(schema_path), (
        f"Schema file for {device_role} role is missing at {schema_path}."
    )


def test_ensure_example_validates_with_base_schema(device_role):
    configs = get_example_configs(device_role)
    if not configs:
        pytest.skip(f"No example configuration found for {device_role}")

    validators = yamale.validators.DefaultValidators.copy()
    validators["ioc_type"] = IOCTypeValidator

    base_schema = yamale.make_schema(
        "roles/deploy_ioc/schema.yml", validators=validators
    )

    for config_path in configs:
        with open(config_path) as fp:
            example_data = yaml.safe_load(fp)
            ioc_name = list(example_data.keys())[0]
            ioc_config = example_data[ioc_name]

        data = yamale.make_data(content=yaml.dump(ioc_config))

        try:
            yamale.validate(base_schema, data, strict=False)
        except Exception as e:
            pytest.fail(
                f"Example {config_path} for {device_role} role "
                f"doesn't conform to the base schema: {e}"
            )


def test_ensure_example_validates_with_role_specific_schema(device_role):
    schema_path = os.path.join("roles/device_roles", device_role, "schema.yml")
    configs = get_example_configs(device_role)

    if not configs:
        pytest.skip(f"No example configuration found for {device_role}")

    validators = yamale.validators.DefaultValidators.copy()
    validators["hostname"] = HostnameValidator

    schema = yamale.make_schema(schema_path, validators=validators)

    for config_path in configs:
        with open(config_path) as fp:
            example_data = yaml.safe_load(fp)
            ioc_name = list(example_data.keys())[0]
            ioc_config = example_data[ioc_name]

        data = yamale.make_data(content=yaml.dump(ioc_config))

        try:
            yamale.validate(schema, data, strict=False)
        except yamale.YamaleError as e:
            pytest.fail(
                f"Example {config_path} for {device_role} role "
                f"doesn't conform to the schema: {e}"
            )


def test_verify_yml_validates_with_schema(device_role):
    verify_files = get_verify_files(device_role)

    if not verify_files:
        pytest.skip(f"No verify.yml found for {device_role}")

    schema = yamale.make_schema("schemas/verify.yml")

    for verify_path in verify_files:
        data = yamale.make_data(verify_path)

        try:
            yamale.validate(schema, data, strict=False)
        except yamale.YamaleError as e:
            pytest.fail(
                f"verify.yml at {verify_path} for {device_role} role "
                f"doesn't conform to schemas/verify.yml: {e}"
            )
