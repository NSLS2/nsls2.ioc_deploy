#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys

import questionary
import tabulate
import yaml


def get_module_list():
    """Return a list of module names from the install_module vars directory."""
    return [
        os.path.splitext(f)[0]
        for f in os.listdir(os.path.join("roles", "install_module", "vars"))
    ]


def get_role_list():
    """Return a list of role names from the deploy_ioc vars directory."""
    return [
        os.path.splitext(f)[0]
        for f in os.listdir(os.path.join("roles", "deploy_ioc", "vars"))
    ]


def add_module():
    """Interactively add a new module configuration file to install_module vars.
    Prompts user for module details and writes a new YAML config file.
    Returns the new module name-version string.
    """
    module_name = questionary.text(
        "Enter the name of the new module (e.g., 'ADKinetix'):",
    ).unsafe_ask()

    module_version = questionary.text(
        "Enter the git commit hash version for the module (e.g. 05e8a65)",
    ).unsafe_ask()

    url = questionary.text(
        "Enter the git URL for the module (e.g. https://github.com/NSLS2/ADKinetix):",
    ).unsafe_ask()

    is_ad = questionary.confirm(
        "Is this an areaDetector module?", default=False
    ).unsafe_ask()

    module_deps = questionary.checkbox(
        "Select any module dependencies:",
        choices=get_module_list(),
    ).unsafe_ask()

    module_name_ver = f"{module_name.lower()}_{module_version}"

    module_config = {
        module_name_ver: {
            "name": module_name,
            "version": module_version,
            "url": url,
            "include_base_ad_config": is_ad,
            "module_deps": module_deps,
        }
    }

    module_config_path = os.path.join(
        "roles", "install_module", "vars", f"{module_name_ver}.yml"
    )

    with open(module_config_path, "w") as file:
        file.write("---\n\n")
        file.write(f"{module_name_ver}:\n")
        for key, value in module_config[module_name_ver].items():
            if key != "module_deps" and not (
                key == "include_base_ad_config" and not value
            ):
                file.write(f"  {key}: {value}\n")
            elif key == "module_deps" and len(value) > 0:
                file.write(f"  {key}:\n")
                for dep in value:
                    file.write(f"    - {dep}\n")

    return module_name_ver


def update_module():
    """Interactively update an existing module's version and update all references.
    Prompts user for new version, updates config, and optionally deletes old config.
    """
    module = questionary.select(
        "Select a module to update:", choices=get_module_list()
    ).unsafe_ask()

    new_version = questionary.text(
        "Enter the new version for the module:",
    ).unsafe_ask()

    old_module_config_path = os.path.join(
        "roles", "install_module", "vars", f"{module}.yml"
    )
    with open(old_module_config_path) as file:
        old_module_config = yaml.safe_load(file)

    old_module_name_ver = list(old_module_config.keys())[0]
    module_config = old_module_config[old_module_name_ver]
    module_base_name = old_module_name_ver.rsplit("_", 1)[0]
    module_config["version"] = new_version
    new_module_name_ver = f"{module_base_name}_{new_version}"
    new_module_config = {new_module_name_ver: module_config}

    new_module_config_path = os.path.join(
        "roles", "install_module", "vars", f"{new_module_name_ver}.yml"
    )

    with open(new_module_config_path, "w") as file:
        yaml.dump(new_module_config, file, default_flow_style=False, sort_keys=False)

    print(f"Updating {module_base_name} to {new_version} for all dependant modules...")
    module_var_files = [
        os.path.join("roles", "install_module", "vars", file)
        for file in os.listdir(os.path.join("roles", "install_module", "vars"))
        if file != f"{old_module_name_ver}.yml"
    ]
    subprocess.run(
        [
            "sed",
            "-i",
            f"s/{old_module_name_ver}/{new_module_name_ver}/g",
            *module_var_files,
        ]
    )

    print(
        f"Updating {module_base_name} to {new_version} for all dependant ioc types..."
    )
    ioc_vars_files = [
        os.path.join("roles", "deploy_ioc", "vars", file)
        for file in os.listdir(os.path.join("roles", "deploy_ioc", "vars"))
    ]
    subprocess.run(
        [
            "sed",
            "-i",
            f"s/{old_module_name_ver}/{new_module_name_ver}/g",
            *ioc_vars_files,
        ]
    )

    delete_old_module_config = questionary.confirm(
        f"Delete old module config file {old_module_name_ver}.yml?", default=True
    ).unsafe_ask()
    if delete_old_module_config:
        os.remove(old_module_config_path)


def delete_module():
    """Interactively delete a module config if not required by other modules or roles.
    Raises RuntimeError if dependencies exist.
    """
    module = questionary.select(
        "Select a module to update:", choices=get_module_list()
    ).unsafe_ask()

    dependant_modules = []
    dependant_ioc_types = []
    for file in os.listdir(os.path.join("roles", "install_module", "vars")):
        with open(os.path.join("roles", "install_module", "vars", file)) as f:
            module_config = yaml.safe_load(f)
            module_name_ver = list(module_config.keys())[0]
            if module in module_config[module_name_ver]["module_deps"]:
                dependant_modules.append(os.path.splitext(file)[0])

    for file in os.listdir(os.path.join("roles", "deploy_ioc", "vars")):
        with open(os.path.join("roles", "deploy_ioc", "vars", file)) as f:
            ioc_config = yaml.safe_load(f)
            if ioc_config["deploy_ioc_required_module"] == module:
                dependant_ioc_types.append(os.path.splitext(file)[0])
    if dependant_modules or dependant_ioc_types:
        raise RuntimeError(
            f"Cannot delete {module} as it is required by the following modules: ",
            f"{', '.join(dependant_modules)} and IOC types: ",
            f"{', '.join(dependant_ioc_types)}.",
        )

    module_path = os.path.join("roles", "install_module", "vars", f"{module}.yml")
    os.remove(module_path)


def add_role():
    """Interactively add a new IOC role and its configuration files.
    Creates role config, example, schema, README, and template files.
    """
    role_name = questionary.text(
        "Enter the name of the new role (e.g., 'sr570'):",
    ).unsafe_ask()
    role_name_actual = role_name.lower()
    if role_name_actual != role_name:
        print(f"Role name '{role_name}' has been lowercased: '{role_name_actual}'.")

    role_var_file_path = os.path.join(
        "roles", "deploy_ioc", "vars", f"{role_name_actual}.yml"
    )

    if role_name_actual in get_role_list() or os.path.exists(role_var_file_path):
        raise RuntimeError(
            f"Role '{role_name_actual}' already exists. ",
            "Please choose a different name, or delete the existing role first.",
        )

    ioc_type_config = {}

    standard_st_cmd = questionary.confirm(
        "Should this role use standard st.cmd (epicsEnv/base/common/postInit)?",
        default=True,
    ).unsafe_ask()
    if not standard_st_cmd:
        ioc_type_config["deploy_ioc_standard_st_cmd"] = False
    else:
        use_common = questionary.confirm(
            "Should this role use common.cmd? Configures", default=True
        ).unsafe_ask()
        ioc_type_config["deploy_ioc_use_common"] = use_common
        if use_common:
            use_ad = questionary.confirm(
                "Is this role for an areaDetector IOC?", default=False
            ).unsafe_ask()
            ioc_type_config["deploy_ioc_use_ad_common"] = use_ad
        required_module = questionary.select(
            "Select the required module for this IOC type:",
            choices=get_module_list() + ["new"],
        ).unsafe_ask()
        if required_module == "new":
            required_module = add_module()
        ioc_type_config["deploy_ioc_required_module"] = required_module
        executable = questionary.text(
            "Enter the name of the IOC executable. Depends on required module:",
        ).unsafe_ask()
        ioc_type_config["deploy_ioc_executable"] = executable

    with open(role_var_file_path, "w") as file:
        file.write("---\n\n")
        yaml.safe_dump(ioc_type_config, file, default_flow_style=False, sort_keys=False)

    if not standard_st_cmd:
        return

    role_path = os.path.join("roles/device_roles", role_name_actual)
    os.makedirs(role_path, exist_ok=True)
    for subdir in ["templates", "tasks"]:
        os.makedirs(os.path.join(role_path, subdir), exist_ok=True)

    with open(os.path.join(role_path, "example.yml"), "w") as file:
        file.write("---\n\n")
        example_config = {
            f"{role_name_actual}-01": {
                "type": role_name_actual,
                "environment": {
                    "ENGINEER": "C. Engineer",
                    "PREFIX": "XF:31ID1-ES{" + role_name_actual.upper() + ":01}",
                },
            }
        }
        yaml.safe_dump(example_config, file, default_flow_style=False, sort_keys=False)

    with open(os.path.join(role_path, "schema.yml"), "w") as file:
        file.write("---\n\n")
        schema_config = {
            "type": f'enum("{role_name_actual}")',
            "environment": {
                "ENGINEER": "str()",
                "PREFIX": "str()",
            },
        }
        yaml.safe_dump(schema_config, file, default_flow_style=False, sort_keys=False)

    with open(os.path.join(role_path, "README.md"), "w") as file:
        file.write(f"# {role_name}\n\n")
        file.write(f"Ansible role for deploying {role_name} IOC instances.\n")

    with open(os.path.join(role_path, "tasks", "main.yml"), "w") as file:
        file.write(f"---\n# Tasks for {role_name} role\n")
        file.write("""
- name: Install base.cmd
  ansible.builtin.template:
    src: templates/base.cmd.j2
    dest: "{{ deploy_ioc_ioc_directory }}/iocBoot/base.cmd"
    mode: "0664"
    owner: "{{ host_config.softioc_user }}"
    group: "{{ host_config.softioc_group }}"
""")

    with open(os.path.join(role_path, "templates", "base.cmd.j2"), "w") as file:
        file.write(
            '\ndbLoadDatabase("{{ deploy_ioc_template_root_path }}/dbd/{{ deploy_ioc_executable }}.dbd")\n'  # noqa: E501
        )
        file.write(
            "{{ deploy_ioc_executable }}_registerRecordDeviceDriver(pdbbase)\n\n"
        )
        file.write(f"# {role_name} specific commands\n")


def update_role():
    """Roles cannot be updated. Raises NotImplementedError."""
    raise NotImplementedError("Roles cannot be updated.")


def delete_role():
    """Interactively delete a role and its configuration files."""
    role = questionary.select(
        "Select a role to delete:", choices=get_role_list()
    ).unsafe_ask()

    role_path = os.path.join("roles/device_roles", role)
    role_vars_path = os.path.join("roles", "deploy_ioc", "vars", f"{role}.yml")

    shutil.rmtree(role_path)
    os.remove(role_vars_path)

    print(f"Role {role} and its configuration have been deleted.")


def report():
    """Print a report of all modules and roles"""

    print("\nDeployable modules:\n")
    modules = {}
    for module in get_module_list():
        module_name, ver = tuple(module.rsplit("_", 1))
        if module_name not in modules:
            modules[module_name] = []
        modules[module_name].append(ver)

    print(
        tabulate.tabulate(
            [(k, ", ".join(v)) for k, v in modules.items()],
            headers=["Module", "Versions"],
            tablefmt="simple",
        )
    )

    print("\nDeployable IOC roles:\n")
    for role in get_role_list():
        print(f" - {role}")

    print("\nNumber of deployable modules:", len(get_module_list()))
    print("Number of deployable IOC roles:", len(get_role_list()))


if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Usage: manage_collection.py <action> [target]")
        print("Actions: add, delete, update, report")
        print("Targets: role, module")
        sys.exit(1)
    action = sys.argv[1]
    if action == "report":
        func = report
    else:
        target = sys.argv[2]
        func = getattr(sys.modules[__name__], f"{action}_{target}")
    try:
        func()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
