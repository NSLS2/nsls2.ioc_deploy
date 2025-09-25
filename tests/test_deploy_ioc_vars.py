import os

import pytest
import yamale
import yaml

DEPLOY_IOC_VARS_FILES = [
    os.path.splitext(f)[0]
    for f in os.listdir("roles/deploy_ioc/vars")
    if f.endswith(".yml")
]

INSTALL_MODULE_FILES = [
    os.path.splitext(f)[0]
    for f in os.listdir("roles/install_module/vars")
    if f.endswith(".yml")
]


pytestmark = pytest.mark.parametrize(
    "deploy_ioc_var_file", DEPLOY_IOC_VARS_FILES, indirect=True
)


def test_deploy_ioc_var_file_has_matching_role(deploy_ioc_var_file):
    assert os.path.exists(os.path.join("roles/device_roles", deploy_ioc_var_file.name))


def test_deploy_ioc_var_files_valid(deploy_ioc_var_file, module_name_validator):
    if deploy_ioc_var_file.data:
        data = yamale.make_data(content=yaml.dump(deploy_ioc_var_file.data))
        validators = yamale.validators.DefaultValidators.copy()
        validators["module_name"] = module_name_validator
        schema = yamale.make_schema(
            "schemas/device_specific_vars.yml", validators=validators
        )
        try:
            yamale.validate(schema, data)
        except Exception as e:
            pytest.fail(f"YAML validation failed: {e}")


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
