import os
import re

import pytest
import yamale
import yaml

REQUIRED_KEYS: dict[str, type] = {
    "name": str,
    "url": str,
    "version": str,
}

OPTIONAL_KEYS: dict[str, type] = {
    "include_base_ad_config": bool,
    "module_deps": list,
    "pkg_deps": list,
    "epics_deps": list,
    "compilation_command": str,
    "config": dict,
    "overwrite_release": bool,
    "overwrite_config_site": bool,
    "use_token": bool,
}

INSTALL_MODULE_FILES = [
    os.path.splitext(f)[0]
    for f in os.listdir("roles/install_module/vars")
    if f.endswith(".yml")
]


pytestmark = pytest.mark.parametrize(
    "install_module_var_file", INSTALL_MODULE_FILES, indirect=True
)


class URLValidator(yamale.validators.Validator):
    tag = "url"

    def _is_valid(self, value: str) -> bool:
        return value.startswith("http://") or value.startswith("https://")


class GitCommitHashValidator(yamale.validators.Validator):
    """
    A Git commit hash typically consists of 7 hexadecimal characters.
    Git can extend this length for uniqueness, but 7 is the common default.
    This regex checks for 7 to 40 hexadecimal characters.
    The 're.IGNORECASE' flag makes the match case-insensitive for hex characters.
    """

    tag = "git_commit_hash"

    def _is_valid(self, value: str) -> bool:
        return bool(re.fullmatch(r"^[0-9a-fA-F]{7,40}$", value))


def test_install_module_vars_files_valid(
    install_module_var_file, module_name_validator
):
    assert len(list(install_module_var_file.data.keys())) == 1
    assert list(install_module_var_file.data.keys())[0] == install_module_var_file.name

    install_module_config_data = install_module_var_file.data[
        install_module_var_file.name
    ]

    validators = yamale.validators.DefaultValidators.copy()
    validators["url"] = URLValidator
    validators["module_name"] = module_name_validator
    validators["git_commit_hash"] = GitCommitHashValidator

    data = yamale.make_data(content=yaml.dump(install_module_config_data))
    default_schema = yamale.make_schema(
        "schemas/install_module.yml", validators=validators
    )
    latest_schema = yamale.make_schema(
        "schemas/install_module_latest.yml", validators=validators
    )
    try:
        if install_module_var_file.name.endswith("_latest"):
            yamale.validate(latest_schema, data, strict=False)
        else:
            yamale.validate(default_schema, data, strict=False)
    except Exception as e:
        pytest.fail(
            f"roles/install_module/vars/{install_module_var_file.name}.yml "
            f"doesn't conform to the schema: {e}"
        )


def test_install_module_vars_files_all_module_deps_exist(
    install_module_var_file,
):
    if "module_deps" in install_module_var_file.data[install_module_var_file.name]:
        for module_dep in install_module_var_file.data[install_module_var_file.name][
            "module_deps"
        ]:
            assert module_dep in INSTALL_MODULE_FILES


def test_ensure_version_suffixed_unless_latest(install_module_var_file):
    install_module_config = install_module_var_file.data[install_module_var_file.name]

    if install_module_var_file.name.endswith("_latest"):
        pytest.skip("Allow latest versions to skip version suffix validation")
    else:
        assert install_module_var_file.name.endswith(install_module_config["version"])
