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
# set -o errexit  # Exit on error
# set -o nounset  # Error on unset variables
# set -o pipefail # Error if a pipe fails
set -euo pipefail

# 2. LOGGING HELPERS
# Send informational text to stderr (file descriptor 2)
# This keeps stdout clean for machine parsing if needed.
log() {
  echo "[INFO] $*" >&2
}

err() {
  echo "[ERROR] $*" >&2
}

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") --service <name>

Options:
  -s, --service   Name of the Homebrew service (required)
  -h, --help      Show help message
EOF
  exit 1
}

# 3. HELPER FUNCTIONS
# Returns 0 (true) if running, 1 (false) if not.
is_service_running() {
  local service_name="$1"

  # We use quiet grep (-q).
  # We match the service name at the start of the line to avoid partial matches.
  if brew services list | grep -q "^${service_name}.*started"; then
    return 0
  else
    return 1
  fi
}

start_service() {
  local service_name="$1"

  log "Attempting to start ${service_name}..."

  # Capture output to avoid clutter, only show if error occurs
  if output=$(brew services start "${service_name}" 2>&1); then
    log "✅ Successfully started ${service_name}."
  else
    err "💀 Failed to start ${service_name}."
    err "Details: ${output}"
    return 1
  fi
}

# 4. MAIN LOGIC
main() {
  local service=""

  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -s|--service)
        service="$2"
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

  # Validate input
  if [[ -z "${service}" ]]; then
    err "Service name is required."
    usage
  fi

  log "Checking status of ${service}..."

  # Logic flow
  if is_service_running "${service}"; then
    log "✅ ${service} is already running."
  else
    log "❌ ${service} is stopped."
    start_service "${service}"
  fi
}

# Execute main
main "$@"
