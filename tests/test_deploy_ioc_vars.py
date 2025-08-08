import os

import pytest

OPTIONAL_KEYS: dict[str, type] = {
    "deploy_ioc_post_deploy_step": str,
    "deploy_ioc_template_root_path": str,
    "deploy_ioc_executable": str,
    "deploy_ioc_standard_st_cmd": bool,
    "deploy_ioc_standard_post_init": bool,
    "deploy_ioc_use_common": bool,
    "deploy_ioc_load_as_substitutions": bool,
    "deploy_ioc_manage_iocs_nextport": int,
    "deploy_ioc_as_dir_name": str,
    "deploy_ioc_device_specific_env": dict,
    "deploy_ioc_required_module": str,
    "deploy_ioc_use_ad_common": bool,
    "deploy_ioc_req_files": list,
}

DEPLOY_IOC_VARS_FILES = [
    os.path.splitext(f)[0]
    for f in os.listdir("roles/deploy_ioc/vars")
    if f.endswith(".yml")
]

pytestmark = pytest.mark.parametrize(
    "deploy_ioc_var_file", DEPLOY_IOC_VARS_FILES, indirect=True
)


def test_deploy_ioc_var_file_has_matching_role(deploy_ioc_var_file):
    assert os.path.exists(os.path.join("roles", deploy_ioc_var_file.name))


def test_deploy_ioc_var_files_valid(deploy_ioc_var_file):
    if deploy_ioc_var_file.data:
        for key in deploy_ioc_var_file.data:
            assert key in OPTIONAL_KEYS
            assert type(deploy_ioc_var_file.data[key]) is OPTIONAL_KEYS[key]


def test_deploy_ioc_var_file_required_module_exists(deploy_ioc_var_file):
    if (
        deploy_ioc_var_file.data
        and "deploy_ioc_required_module" in deploy_ioc_var_file.data
    ):
        if deploy_ioc_var_file.data["deploy_ioc_required_module"]:
            assert os.path.exists(
                os.path.join(
                    "roles/install_module/vars",
                    f"{deploy_ioc_var_file.data['deploy_ioc_required_module']}.yml",
                )
            )
