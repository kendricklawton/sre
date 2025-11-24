#!/usr/bin/env bash
#
# analyze_logs.sh
#
# Description:
#   Parses a web server log file to extract the top N IP addresses.
#   Follows Google Shell Style Guide.
#
# Usage:
#   ./analyze_logs.sh --file <path> [--limit <number>]

# 1. DEFENSIVE BASHERY (Strict Mode)
# -e: Exit immediately if a command exits with a non-zero status.
# -u: Treat unset variables as an error.
# -o pipefail: Return the exit status of the last command in the pipe that failed.
# set -o errexit
# set -o nounset
# set -o pipefail
set -euo pipefail

# 2. CONSTANTS & DEFAULTS
# Use 'readonly' to prevent accidental variable overwrites.
readonly DEFAULT_LIMIT=5

# 3. LOGGING FUNCTIONS
# Send logs to stderr so they don't mess up the data output (stdout).
err() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" >&2
}

log() {
  echo "[INFO]: $*" >&2
}

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") --file <path> [--limit <number>]

Arguments:
  -f, --file    Path to the log file (required)
  -l, --limit   Number of top IPs to show (default: ${DEFAULT_LIMIT})
  -h, --help    Show this help message
EOF
  exit 1
}

# 4. BUSINESS LOGIC
analyze_logs() {
  local file="$1"
  local limit="$2"

  # Validate file existence strictly
  if [[ ! -f "${file}" ]]; then
    err "File not found: ${file}"
    exit 1
  fi

  log "Processing ${file} with limit ${limit}..."

  # The pipeline
  # We catch errors here because of 'set -o pipefail'
  awk '{print $1}' "${file}" \
    | sort \
    | uniq -c \
    | sort -nr \
    | head -n "${limit}"
}

# 5. MAIN EXECUTION
main() {
  local log_file=""
  local limit="${DEFAULT_LIMIT}"

  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -f|--file)
        log_file="$2"
        shift 2
        ;;
      -l|--limit)
        limit="$2"
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

  # Validation
  if [[ -z "${log_file}" ]]; then
    err "Missing required argument: --file"
    usage
  fi

  # Execute Logic
  analyze_logs "${log_file}" "${limit}"
}

# Invoke main with all arguments
main "$@"
