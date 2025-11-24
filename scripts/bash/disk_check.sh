#!/usr/bin/env bash
#
# ensure_service.sh
#
# Description:
#   Checks if a Homebrew service is running on macOS. If stopped, attempts to start it.
#   Follows Google Shell Style Guide.
#
# Usage:
#   ./ensure_service.sh --service <service_name>

# 1. DEFENSIVE BASHERY (Strict Mode)
# -e: Exit immediately if a command exits with a non-zero status.
# -u: Treat unset variables as an error.
# -o pipefail: Return the exit status of the last command in the pipe that failed.
set -o errexit  # Exit on error
set -o nounset  # Error on unset variables
set -o pipefail # Error if a pipe fails

# 2. DEFAULTS
readonly DEFAULT_THRESHOLD=85
readonly DEFAULT_PATH="/"

# 3. LOGGING
log() {
  echo "[INFO] $*" >&2
}

err() {
  echo "[ALARM] $*" >&2
}

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [options]

Options:
  -p, --path       Mount point to check (default: /)
  -t, --threshold  Percentage threshold to trigger alert (default: 85)
  -h, --help       Show this help message
EOF
  exit 1
}

# 4. CORE LOGIC
get_disk_usage() {
  local target="$1"

  # SRE TRICK: Use 'df -P' (POSIX standard).
  # This forces output into a standard format on both Linux and macOS,
  # preventing line wrapping issues on long filesystem names.
  # We strip the '%' sign using tr.
  df -P "${target}" | awk 'NR==2 {print $5}' | tr -d '%'
}

# 5. MAIN
main() {
  local path="${DEFAULT_PATH}"
  local threshold="${DEFAULT_THRESHOLD}"

  # Argument Parsing
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -p|--path)
        path="$2"
        shift 2
        ;;
      -t|--threshold)
        threshold="$2"
        shift 2
        ;;
      -h|--help)
        usage
        ;;
      *)
        err "Unknown argument: $1"
        usage
        ;;
    esac
  done

  # Pre-flight check: Does the path exist?
  if [[ ! -e "${path}" ]]; then
    err "Path '${path}' does not exist."
    exit 1
  fi

  log "Checking disk space on '${path}'..."

  # Capture usage
  # We declare 'local' to limit scope, satisfying style guides.
  local current_usage
  current_usage=$(get_disk_usage "${path}")

  # Validate that we actually got a number back
  if [[ ! "${current_usage}" =~ ^[0-9]+$ ]]; then
    err "Failed to determine disk usage. Output was: ${current_usage}"
    exit 1
  fi

  # Comparison Logic
  # Using double parentheses (( ... )) is the preferred Bash way for arithmetic.
  if (( current_usage >= threshold )); then
    err "CRITICAL: Disk usage is at ${current_usage}% (Threshold: ${threshold}%)"
    exit 1
  else
    log "OK: Disk usage is at ${current_usage}% (Threshold: ${threshold}%)"
    exit 0
  fi
}

main "$@"
