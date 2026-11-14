#!/usr/bin/env bash
set -euo pipefail

# Generate a powerpmac config.yml from legacy IOC files under:
#   <ioc_root>/db/*.substitutions
#   <ioc_root>/iocBoot/{epicsEnv.cmd,st.cmd|base.cmd}

usage() {
  cat <<'EOF'
Usage:
  powerpmac_config_from_legacy_ioc.sh <ioc_root> [output_config.yml] [config_key]

Arguments:
  ioc_root          Path containing db/ and iocBoot/
  output_config.yml Output path (default: <ioc_root>/config.yml)
  config_key        Top-level YAML key (default: IOCNAME from epicsEnv.cmd, else basename(ioc_root))
EOF
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 || $# -gt 3 ]]; then
  usage
  exit 2
fi

IOC_ROOT="$1"
OUT_FILE="${2:-$IOC_ROOT/config.yml}"

DB_DIR="$IOC_ROOT/db"
BOOT_DIR="$IOC_ROOT/iocBoot"
EPICS_ENV="$BOOT_DIR/epicsEnv.cmd"
ST_CMD="$BOOT_DIR/st.cmd"
BASE_CMD="$BOOT_DIR/base.cmd"

if [[ ! -d "$DB_DIR" || ! -d "$BOOT_DIR" ]]; then
  echo "error: expected $IOC_ROOT to contain db/ and iocBoot/" >&2
  exit 1
fi
if [[ ! -f "$EPICS_ENV" ]]; then
  echo "error: missing $EPICS_ENV" >&2
  exit 1
fi
if [[ ! -f "$ST_CMD" && ! -f "$BASE_CMD" ]]; then
  echo "error: expected one of $ST_CMD or $BASE_CMD" >&2
  exit 1
fi

BOOT_FILE="$ST_CMD"
if [[ ! -f "$BOOT_FILE" ]]; then
  BOOT_FILE="$BASE_CMD"
fi

MOTOR_SUB="$DB_DIR/motor.substitutions"
CS_SUB="$DB_DIR/cs.substitutions"
AUTOHOME_SUB="$DB_DIR/autohome.substitutions"
PMACSTATUS_SUB="$DB_DIR/pmacStatus.substitutions"

if [[ ! -f "$MOTOR_SUB" || ! -f "$PMACSTATUS_SUB" ]]; then
  echo "error: missing required substitutions: motor.substitutions and/or pmacStatus.substitutions" >&2
  exit 1
fi

extract_env() {
  local key="$1"
  local val
  val=$(sed -nE "s/.*epicsEnvSet\(\"${key}\",[[:space:]]*\"([^\"]*)\"\).*/\1/p" "$EPICS_ENV" | head -n1 || true)
  echo "$val"
}

trim_component() {
  local raw="$1"
  echo "$raw" | sed -E 's/^[[:space:]]*\{//; s/[[:space:]]*$//; s/Mtr[[:space:]]*$//; s/\}[[:space:]]*$//'
}

split_axis_macro() {
  local macro="$1"
  local clean component name
  clean=$(trim_component "$macro")
  if [[ "$clean" == *"-Ax:"* ]]; then
    component="${clean%-Ax:*}"
    name="${clean##*-Ax:}"
  else
    component="$clean"
    name="$clean"
  fi
  echo "$component|$name"
}

# Parse a legacy substitution row and print a normalized pipe-separated record.
# Format: P|M|MOTOR|PORT|ADDR|DESC|MRES|EGU
parse_legacy_row() {
  local line="$1"
  awk '
    function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
    {
      # Remove outer braces.
      sub(/^[[:space:]]*\{/, "", $0)
      sub(/\}[[:space:]]*$/, "", $0)
      # Split on comma; legacy files are consistently comma-delimited.
      n = split($0, a, /,/) 
      if (n < 9) next

      p = trim(a[1]); gsub(/^"|"$/, "", p)
      m = trim(a[2]); gsub(/^"|"$/, "", m)
      motor = trim(a[3]); gsub(/^"|"$/, "", motor)
      port = trim(a[4]); gsub(/^"|"$/, "", port)
      addr = trim(a[5]); gsub(/^"|"$/, "", addr)
      desc = trim(a[6]); gsub(/^"|"$/, "", desc)

      # Legacy motor rows include DTYP between DESC and MRES, cs rows too.
      # MRES/EGU positions are stable in old files (8,9 when DTYP exists).
      mres = trim(a[8]); gsub(/^"|"$/, "", mres)
      egu = trim(a[9]); gsub(/^"|"$/, "", egu)

      print p "|" m "|" motor "|" port "|" addr "|" desc "|" mres "|" egu
    }
  ' <<< "$line"
}

readarray -t MOTOR_ROWS < <(grep -E '^[[:space:]]*\{"' "$MOTOR_SUB" || true)
if [[ ${#MOTOR_ROWS[@]} -eq 0 ]]; then
  echo "error: found no motor rows in $MOTOR_SUB" >&2
  exit 1
fi

SYS=$(extract_env "PREFIX")
ENGINEER=$(extract_env "ENGINEER")
CONTROLLER_IP=$(extract_env "CONTROLLER_IP")
NUM_AXES=$(extract_env "NUM_AXES")
IOCNAME=$(extract_env "IOCNAME")

# Derive NUM_AXES from the largest motor address/axis value seen in motor.substitutions.
NUM_AXES_FROM_MOTOR=$(awk '
  function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
  BEGIN { max = 0 }
  /^[[:space:]]*\{"/ {
    line = $0
    sub(/^[[:space:]]*\{/, "", line)
    sub(/\}[[:space:]]*$/, "", line)
    n = split(line, a, /,/) 

    # Legacy motor.substitutions has ADDR as column 5.
    if (n >= 5) {
      v = trim(a[5])
      gsub(/^"|"$/, "", v)
      if (v ~ /^[0-9]+$/ && (v + 0) > max) max = v + 0
    }

    # Be tolerant if an AXIS column is present in other substitution layouts.
    for (i = 1; i <= n; i++) {
      token = trim(a[i])
      gsub(/^"|"$/, "", token)
      if (tolower(token) == "axis" && i < n) {
        av = trim(a[i + 1])
        gsub(/^"|"$/, "", av)
        if (av ~ /^[0-9]+$/ && (av + 0) > max) max = av + 0
      }
    }
  }
  END {
    if (max > 0) print max
  }
' "$MOTOR_SUB")

# Pull controller/system defaults from pmacStatus substitutions first row.
PMAC_ROW=$(grep -E '^[[:space:]]*\{"' "$PMACSTATUS_SUB" | head -n1 || true)
if [[ -n "$PMAC_ROW" ]]; then
  PMAC_FIELDS=$(awk '
    function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
    {
      sub(/^[[:space:]]*\{/, "", $0)
      sub(/\}[[:space:]]*$/, "", $0)
      n = split($0, a, /,/) 
      if (n < 6) exit
      sys = trim(a[1]); gsub(/^"|"$/, "", sys)
      pmac = trim(a[2]); gsub(/^"|"$/, "", pmac)
      naxes = trim(a[6]); gsub(/^"|"$/, "", naxes)
      print sys "|" pmac "|" naxes
    }
  ' <<< "$PMAC_ROW")
  CT_SYS="${PMAC_FIELDS%%|*}"
  REST="${PMAC_FIELDS#*|}"
  CONTROLLER="${REST%%|*}"
  NAXES_FROM_SUB="${REST#*|}"
else
  CT_SYS=""
  CONTROLLER=""
  NAXES_FROM_SUB=""
fi

if [[ -z "$SYS" ]]; then
  FIRST_FIELDS=$(parse_legacy_row "${MOTOR_ROWS[0]}")
  SYS="${FIRST_FIELDS%%|*}"
fi
if [[ -z "$CT_SYS" ]]; then
  CT_PREFIX=$(extract_env "CT_PREFIX")
  CT_SYS="${CT_PREFIX%%\{*}"
fi
if [[ -z "$CONTROLLER" ]]; then
  CT_PREFIX=$(extract_env "CT_PREFIX")
  CONTROLLER="${CT_PREFIX#*\{}"
  CONTROLLER="${CONTROLLER%\}*}"
fi
if [[ -n "$NUM_AXES_FROM_MOTOR" ]]; then
  NUM_AXES="$NUM_AXES_FROM_MOTOR"
elif [[ -z "$NUM_AXES" ]]; then
  NUM_AXES="$NAXES_FROM_SUB"
fi
if [[ -z "$NUM_AXES" ]]; then
  NUM_AXES="8"
fi
if [[ -z "$ENGINEER" ]]; then
  ENGINEER="Unknown"
fi

# Controller poll periods from pmacCreateController(..., moving, idle)
CTRL_LINE=$(grep -E '^[[:space:]]*pmacCreateController\(' "$BOOT_FILE" | head -n1 || true)
MOVING_POLL_PERIOD=$(awk -F',' '{gsub(/[[:space:])]/, "", $5); print $5}' <<< "$CTRL_LINE" 2>/dev/null || true)
IDLE_POLL_PERIOD=$(awk -F',' '{gsub(/[[:space:])]/, "", $6); print $6}' <<< "$CTRL_LINE" 2>/dev/null || true)
MOVING_POLL_PERIOD="${MOVING_POLL_PERIOD:-100}"
IDLE_POLL_PERIOD="${IDLE_POLL_PERIOD:-1000}"

# Optional top-level YAML key.
CONFIG_KEY="${3:-${IOCNAME:-$(basename "$IOC_ROOT")}}"

# Parse disabled limits from boot file.
DISABLE_ALL_LIMITS="false"
declare -A DISABLE_AXIS
if grep -Eq '^[[:space:]]*pmacDisableLimitsCheck\([^#]*,[[:space:]]*0[[:space:]]*,[[:space:]]*1[[:space:]]*\)' "$BOOT_FILE"; then
  DISABLE_ALL_LIMITS="true"
else
  while IFS= read -r line; do
    axis=$(sed -nE 's/^[[:space:]]*pmacDisableLimitsCheck\([^,]+,[[:space:]]*([0-9]+)[[:space:]]*,[[:space:]]*0[[:space:]]*\).*/\1/p' <<< "$line")
    if [[ -n "$axis" ]]; then
      DISABLE_AXIS["$axis"]=true
    fi
  done < <(grep -E '^[[:space:]]*pmacDisableLimitsCheck\(' "$BOOT_FILE" || true)
fi

# Parse coordinate systems and axes count.
declare -A CS_MOTION_PROG
while IFS= read -r line; do
  num=$(sed -nE 's/^[[:space:]]*pmacCreateCS\("CS([0-9]+)"[[:space:]]*,[[:space:]]*"[^"]+"[[:space:]]*,[[:space:]]*([0-9]+)[[:space:]]*,[[:space:]]*([0-9]+)\).*/\2/p' <<< "$line")
  prog=$(sed -nE 's/^[[:space:]]*pmacCreateCS\("CS([0-9]+)"[[:space:]]*,[[:space:]]*"[^"]+"[[:space:]]*,[[:space:]]*([0-9]+)[[:space:]]*,[[:space:]]*([0-9]+)\).*/\3/p' <<< "$line")
  if [[ -n "$num" && -n "$prog" ]]; then
    CS_MOTION_PROG["$num"]="$prog"
  fi
done < <(grep -E '^[[:space:]]*pmacCreateCS\(' "$BOOT_FILE" || true)

declare -A CS_NUM_AXES
while IFS= read -r line; do
  cs=$(sed -nE 's/^[[:space:]]*pmacCreateCSAxes\("CS([0-9]+)"[[:space:]]*,[[:space:]]*([0-9]+)\).*/\1/p' <<< "$line")
  n=$(sed -nE 's/^[[:space:]]*pmacCreateCSAxes\("CS([0-9]+)"[[:space:]]*,[[:space:]]*([0-9]+)\).*/\2/p' <<< "$line")
  if [[ -n "$cs" && -n "$n" ]]; then
    CS_NUM_AXES["$cs"]="$n"
  fi
done < <(grep -E '^[[:space:]]*pmacCreateCSAxes\(' "$BOOT_FILE" || true)

# Parse autohome for virtual axis PLC mapping.
declare -A AUTOHOME_PLC
if [[ -f "$AUTOHOME_SUB" ]]; then
  while IFS= read -r line; do
    parsed=$(awk '
      function trim(s){gsub(/^[ \t]+|[ \t]+$/, "", s); return s}
      {
        sub(/^[[:space:]]*\{/, "", $0)
        sub(/\}[[:space:]]*$/, "", $0)
        n = split($0, a, /,/) 
        if (n < 4) next
        dev = trim(a[2]); gsub(/^"|"$/, "", dev)
        plc = trim(a[3]); gsub(/^"|"$/, "", plc)
        print dev "|" plc
      }
    ' <<< "$line")
    dev="${parsed%%|*}"
    plc="${parsed#*|}"
    if [[ -n "$dev" && -n "$plc" ]]; then
      dev_clean=$(trim_component "$dev")
      AUTOHOME_PLC["$dev_clean"]="$plc"
    fi
  done < <(grep -E '^[[:space:]]*\{"' "$AUTOHOME_SUB" || true)
fi

# Build real axes from motor.substitutions (MOTOR not starting with CS).
real_axes=()
for row in "${MOTOR_ROWS[@]}"; do
  parsed=$(parse_legacy_row "$row")
  m_macro=$(cut -d'|' -f2 <<< "$parsed")
  motor_port=$(cut -d'|' -f3 <<< "$parsed")
  axis_num=$(cut -d'|' -f5 <<< "$parsed")
  desc=$(cut -d'|' -f6 <<< "$parsed")
  mres=$(cut -d'|' -f7 <<< "$parsed")
  egu=$(cut -d'|' -f8 <<< "$parsed")

  # Real motors are wired to controller port (e.g. M0), not CS ports.
  if [[ "$motor_port" == CS* ]]; then
    continue
  fi

  split=$(split_axis_macro "$m_macro")
  component="${split%%|*}"
  name="${split#*|}"

  disable="false"
  if [[ "$DISABLE_ALL_LIMITS" == "true" || -n "${DISABLE_AXIS[$axis_num]:-}" ]]; then
    disable="true"
  fi

  real_axes+=("$name|$axis_num|$component|$desc|$mres|$egu|$disable")
done

# Build virtual axes from cs.substitutions if present.
virtual_axes=()
if [[ -f "$CS_SUB" ]]; then
  while IFS= read -r row; do
    parsed=$(parse_legacy_row "$row")
    m_macro=$(cut -d'|' -f2 <<< "$parsed")
    motor_port=$(cut -d'|' -f3 <<< "$parsed")
    axis_num=$(cut -d'|' -f5 <<< "$parsed")
    desc=$(cut -d'|' -f6 <<< "$parsed")
    mres=$(cut -d'|' -f7 <<< "$parsed")
    egu=$(cut -d'|' -f8 <<< "$parsed")

    # Virtual axes are declared with MOTOR=CS<n>.
    if [[ "$motor_port" != CS* ]]; then
      continue
    fi

    cs_num="${motor_port#CS}"
    split=$(split_axis_macro "$m_macro")
    component="${split%%|*}"
    name="${split#*|}"
    clean=$(trim_component "$m_macro")
    home_plc="${AUTOHOME_PLC[$clean]:-0}"

    virtual_axes+=("$name|$axis_num|$cs_num|$component|$desc|$mres|$egu|$home_plc")
  done < <(grep -E '^[[:space:]]*\{"' "$CS_SUB" || true)
fi

mkdir -p "$(dirname "$OUT_FILE")"
{
  echo "---"
  echo "$CONFIG_KEY:"
  echo "  type: powerpmac"
  echo "  environment:"
  echo "    SYS: \"$SYS\""
  echo "    CONTROLLER: \"$CONTROLLER\""
  echo "    DEV: \"{\$(CONTROLLER)}\""
  echo "    CT_SYS: \"$CT_SYS\""
  echo "    NUM_AXES: $NUM_AXES"
  echo "    ENGINEER: \"$ENGINEER\""
  echo "    MOVING_POLL_PERIOD: $MOVING_POLL_PERIOD"
  echo "    IDLE_POLL_PERIOD: $IDLE_POLL_PERIOD"
  echo "    CONTROLLER_IP: \"$CONTROLLER_IP\""

  if [[ "$DISABLE_ALL_LIMITS" == "true" ]]; then
    echo
    echo "  disable_all_limits: true"
  fi

  cs_has_complete_data="false"
  cs_keys=("${!CS_MOTION_PROG[@]}")
  for cs in "${cs_keys[@]}"; do
    if [[ -n "${CS_NUM_AXES[$cs]:-}" ]]; then
      cs_has_complete_data="true"
      break
    fi
  done

  if [[ "$cs_has_complete_data" == "true" ]]; then
    echo
    echo "  coord_systems:"
    for cs in $(printf "%s\n" "${cs_keys[@]}" | sort -n); do
      if [[ -z "${CS_NUM_AXES[$cs]:-}" ]]; then
        continue
      fi
      num_axes="${CS_NUM_AXES[$cs]}"
      echo "    - num: $cs"
      echo "      motion_prog: ${CS_MOTION_PROG[$cs]}"
      echo "      num_axes: $num_axes"
    done
  fi

  echo
  echo "  axes:"
  for a in "${real_axes[@]}"; do
    name=$(cut -d'|' -f1 <<< "$a")
    num=$(cut -d'|' -f2 <<< "$a")
    component=$(cut -d'|' -f3 <<< "$a")
    desc=$(cut -d'|' -f4 <<< "$a")
    mres=$(cut -d'|' -f5 <<< "$a")
    egu=$(cut -d'|' -f6 <<< "$a")
    disable=$(cut -d'|' -f7 <<< "$a")

    echo "    - name: \"$name\""
    echo "      num: $num"
    echo "      component: $component"
    echo "      desc: \"$desc\""
    echo "      mres: $mres"
    echo "      egu: \"$egu\""
    echo "      disable_limits: $disable"
  done

  if [[ ${#virtual_axes[@]} -gt 0 ]]; then
    echo
    echo "  virtual_axes:"
    for v in "${virtual_axes[@]}"; do
      name=$(cut -d'|' -f1 <<< "$v")
      num=$(cut -d'|' -f2 <<< "$v")
      cs=$(cut -d'|' -f3 <<< "$v")
      component=$(cut -d'|' -f4 <<< "$v")
      desc=$(cut -d'|' -f5 <<< "$v")
      mres=$(cut -d'|' -f6 <<< "$v")
      egu=$(cut -d'|' -f7 <<< "$v")
      home_plc=$(cut -d'|' -f8 <<< "$v")

      echo "    - name: \"$name\""
      echo "      num: $num"
      echo "      cs: $cs"
      echo "      component: $component"
      echo "      desc: \"$desc\""
      echo "      mres: $mres"
      echo "      egu: \"$egu\""
      echo "      home_plc: $home_plc"
    done
  fi
} > "$OUT_FILE"

echo "Wrote $OUT_FILE"
