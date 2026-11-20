#!/bin/bash
# Test containers lack udev; create the rules dir so the PICam udev rule gets installed.
set -euo pipefail
mkdir -p /etc/udev/rules.d
