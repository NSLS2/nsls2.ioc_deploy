#!/usr/bin/env python3
"""Generate markdown tables of supported modules and device roles for docs."""

from pathlib import Path

import yaml


def generate_module_table() -> str:
    """Generate a markdown table of all installable modules."""
    vars_dir = Path("roles/install_module/vars")
    modules: dict[str, list[dict]] = {}

    for f in sorted(vars_dir.glob("*.yml")):
        with open(f) as fp:
            data = yaml.safe_load(fp)
        key = list(data.keys())[0]
        config = data[key]
        base_name = key.rsplit("_", 1)[0]
        version = config.get("version", key.rsplit("_", 1)[-1])

        if base_name not in modules:
            modules[base_name] = []
        modules[base_name].append(
            {
                "version": version,
                "name": config.get("name", base_name),
                "url": config.get("url", ""),
                "is_ad": config.get("include_base_ad_config", False),
            }
        )

    lines = [
        "| Module | Versions | Type | Repository |",
        "|--------|----------|------|------------|",
    ]
    for _, versions in sorted(modules.items()):
        display_name = versions[0]["name"]
        version_list = ", ".join(f"`{v['version']}`" for v in versions)
        mod_type = "areaDetector" if versions[0]["is_ad"] else "Standard"
        url = versions[0]["url"]
        repo_link = f"[source]({url})" if url else ""
        lines.append(f"| {display_name} | {version_list} | {mod_type} | {repo_link} |")

    return "\n".join(lines)


def generate_role_table() -> str:
    """Generate a markdown table of all device roles."""
    vars_dir = Path("roles/deploy_ioc/vars")
    lines = [
        "| Role | Required Module | Uses AD Common | Uses Common |",
        "|------|----------------|----------------|-------------|",
    ]

    for f in sorted(vars_dir.glob("*.yml")):
        role_name = f.stem
        with open(f) as fp:
            data = yaml.safe_load(fp)

        required_module = data.get("deploy_ioc_required_module", "—")
        use_ad = "Yes" if data.get("deploy_ioc_use_ad_common", False) else "No"
        use_common = "Yes" if data.get("deploy_ioc_use_common", True) else "No"

        # Check if standard_st_cmd is false
        if not data.get("deploy_ioc_standard_st_cmd", True):
            use_common = "N/A (custom)"

        lines.append(
            f"| `{role_name}` | `{required_module}` | {use_ad} | {use_common} |"
        )

    return "\n".join(lines)


def main():
    docs_file = Path("docs/reference/supported-modules.md")
    content = docs_file.read_text()

    module_table = generate_module_table()
    role_table = generate_role_table()

    # Replace module table
    start_marker = "<!-- BEGIN_MODULE_TABLE -->"
    end_marker = "<!-- END_MODULE_TABLE -->"
    start_idx = content.index(start_marker) + len(start_marker)
    end_idx = content.index(end_marker)
    content = content[:start_idx] + "\n" + module_table + "\n" + content[end_idx:]

    # Replace role table
    start_marker = "<!-- BEGIN_ROLE_TABLE -->"
    end_marker = "<!-- END_ROLE_TABLE -->"
    start_idx = content.index(start_marker) + len(start_marker)
    end_idx = content.index(end_marker)
    content = content[:start_idx] + "\n" + role_table + "\n" + content[end_idx:]

    docs_file.write_text(content)
    print(f"Updated {docs_file}")


if __name__ == "__main__":
    main()
