import os

import pytest

DEVICE_ROLES = [role for role in os.listdir("roles/device_roles")]

@pytest.mark.parametrize("device_role", DEVICE_ROLES)
def test_ensure_var_file_for_device_role_exists(device_role):
    var_file_path = os.path.join("roles", "deploy_ioc", "vars", f"{device_role}.yml")
    assert os.path.exists(var_file_path), f"Vars file {var_file_path} not found"
