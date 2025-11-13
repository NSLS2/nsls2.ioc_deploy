import os
import re
import sys

import jinja2
import yaml


# Available in Ansible but not base jinja2
# Implementation based on Ansible's regex_replace filter
def regex_replace(value, pattern, replacement="", ignorecase=False, multiline=False):
    flags = 0
    if ignorecase:
        flags |= re.IGNORECASE
    if multiline:
        flags |= re.MULTILINE
    return re.sub(pattern, replacement, value, flags=flags)


# Create Jinja2 environment with custom filters
env = jinja2.Environment()
env.filters["regex_replace"] = regex_replace


if __name__ == "__main__":
    role = sys.argv[1].strip()
    # Load the example configuration
    with open(f"roles/device_roles/{role}/example.yml") as f:
        example_config = yaml.safe_load(f)
    ioc_name = list(example_config.keys())[0]
    ioc = example_config[ioc_name]
    # Load the templates
    for template_file in os.listdir(f"roles/device_roles/{role}/templates"):
        if template_file.endswith(".substitutions.j2"):
            with open(f"roles/device_roles/{role}/templates/{template_file}") as f:
                print(f"Loading template: {template_file}")
                template = env.from_string(f.read())
            # Parse the template
            parsed_template = template.render(
                environment=ioc["environment"],
                channels=ioc.get("channels", []),
                loops=ioc.get("loops", []),
            )
            print(f"Parsed template: {template_file}\n{'-' * 80}\n")
            print(parsed_template)
            print(f"{'-' * 80}\n")
