from pathlib import Path

import pytest

DEVICE_ROLES_PATH = Path("roles/device_roles")

DEVICE_ROLES = [role.stem for role in DEVICE_ROLES_PATH.iterdir() if role.is_dir()]


@pytest.mark.parametrize("device_role_name", DEVICE_ROLES)
def test_ensure_var_file_for_device_role_exists(device_role_name):
    var_file_path = Path("roles/deploy_ioc/vars") / f"{device_role_name}.yml"
    assert var_file_path.exists(), f"Vars file {var_file_path} not found"


@pytest.mark.parametrize("device_role_name", DEVICE_ROLES)
def test_every_device_role_has_a_readme(device_role_name):
    device_role_path = DEVICE_ROLES_PATH / device_role_name
    readme_path = device_role_path / "README.md"
    assert readme_path.exists(), (
        f"README.md not found for device role: {device_role_name}"
    )
