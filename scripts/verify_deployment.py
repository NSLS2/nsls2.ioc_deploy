#!/usr/bin/env python3
"""
Verify IOC deployment against a declarative verify.yml schema.

Usage:
    verify_deployment.py <verify_yml> <ioc_dir>

The script loads the verify.yml schema and validates the deployment
by reading files directly from the filesystem.
"""

import argparse
import stat
import sys
from pathlib import Path

import yaml


def verify_files_exist(ioc_dir: Path, files: list[str]) -> list[str]:
    """Check that all specified files exist."""
    errors = []
    for f in files:
        path = ioc_dir / f
        if not path.exists():
            errors.append(f"File not found: {path}")
    return errors


def verify_file_contains(
    ioc_dir: Path, file_patterns: dict[str, list[str]]
) -> list[str]:
    """Check that files contain required patterns."""
    errors = []
    for filename, patterns in file_patterns.items():
        path = ioc_dir / filename
        try:
            content = path.read_text()
        except OSError as e:
            errors.append(f"Cannot read file {filename}: {e}")
            continue
        for pattern in patterns:
            if pattern not in content:
                errors.append(f"{filename}: missing required pattern '{pattern}'")
    return errors


def verify_file_not_contains(
    ioc_dir: Path, file_patterns: dict[str, list[str]]
) -> list[str]:
    """Check that files do NOT contain forbidden patterns."""
    errors = []
    for filename, patterns in file_patterns.items():
        path = ioc_dir / filename
        try:
            content = path.read_text()
        except OSError as e:
            errors.append(f"Cannot read file {filename}: {e}")
            continue
        for pattern in patterns:
            if pattern in content:
                errors.append(f"{filename}: contains forbidden pattern '{pattern}'")
    return errors


def verify_permissions(ioc_dir: Path, perms: dict[str, str]) -> list[str]:
    """Check file/directory permissions."""
    errors = []
    for path_str, expected_mode in perms.items():
        full_path = ioc_dir / path_str
        try:
            actual_mode = oct(stat.S_IMODE(full_path.stat().st_mode))
        except OSError as e:
            errors.append(f"Cannot stat {path_str}: {e}")
            continue
        # Normalize: compare as octal strings
        expected_oct = oct(int(expected_mode, 8))
        if expected_oct != actual_mode:
            errors.append(
                f"{path_str}: expected mode {expected_mode}, got {actual_mode}"
            )
    return errors


def verify_ownership(ioc_dir: Path, ownership: dict[str, str]) -> list[str]:
    """Check file/directory ownership."""
    errors = []
    for path_str, expected_owner in ownership.items():
        full_path = ioc_dir / path_str
        try:
            import grp
            import pwd

            st = full_path.stat()
            user = pwd.getpwuid(st.st_uid).pw_name
            group = grp.getgrgid(st.st_gid).gr_name
            actual_owner = f"{user}:{group}"
        except (OSError, KeyError) as e:
            errors.append(f"Cannot get ownership of {path_str}: {e}")
            continue
        if expected_owner != actual_owner:
            errors.append(
                f"{path_str}: expected owner {expected_owner}, got {actual_owner}"
            )
    return errors


def run_verification(verify_yml: Path, ioc_dir: Path) -> bool:
    """Run all verification checks and return True if all pass."""
    with open(verify_yml) as f:
        schema = yaml.safe_load(f)

    verification = schema.get("verification", {})
    all_errors = []

    # files_must_exist
    if "files_must_exist" in verification:
        print("Checking file existence...")
        errors = verify_files_exist(ioc_dir, verification["files_must_exist"])
        all_errors.extend(errors)

    # file_must_contain
    if "file_must_contain" in verification:
        print("Checking file content (must contain)...")
        errors = verify_file_contains(ioc_dir, verification["file_must_contain"])
        all_errors.extend(errors)

    # file_must_not_contain
    if "file_must_not_contain" in verification:
        print("Checking file content (must not contain)...")
        errors = verify_file_not_contains(
            ioc_dir, verification["file_must_not_contain"]
        )
        all_errors.extend(errors)

    # permissions
    if "permissions" in verification:
        print("Checking permissions...")
        errors = verify_permissions(ioc_dir, verification["permissions"])
        all_errors.extend(errors)

    # ownership
    if "ownership" in verification:
        print("Checking ownership...")
        errors = verify_ownership(ioc_dir, verification["ownership"])
        all_errors.extend(errors)

    # Report results
    if all_errors:
        print(f"\nVerification FAILED with {len(all_errors)} error(s):")
        for err in all_errors:
            print(f"  - {err}")
        return False

    print("\nAll verification checks passed.")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Verify IOC deployment against verify.yml schema"
    )
    parser.add_argument("verify_yml", help="Path to verify.yml schema file")
    parser.add_argument("ioc_dir", help="Path to deployed IOC directory")
    args = parser.parse_args()

    verify_yml = Path(args.verify_yml)
    ioc_dir = Path(args.ioc_dir)

    print(f"Verifying deployment:")
    print(f"  Schema: {verify_yml}")
    print(f"  IOC Directory: {ioc_dir}\n")

    if not verify_yml.exists():
        print(f"Error: verify.yml not found: {verify_yml}")
        sys.exit(1)

    if not ioc_dir.exists():
        print(f"Error: IOC directory not found: {ioc_dir}")
        sys.exit(1)

    success = run_verification(verify_yml, ioc_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
