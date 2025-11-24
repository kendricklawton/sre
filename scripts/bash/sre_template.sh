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

# 2. LOGGING HELPERS
log() {
  echo "[INFO] $*" >&2
}

err() {
  echo "[ERROR] $*" >&2
}

# 3. DESTRUCTIVE LOGIC
safe_cleanup() {
  local target_dir="$1"

  log "Request received to clean up: '${target_dir}'"

  # --- SRE STANDARD SAFETY BLOCK ---
  # Check 1: Is the variable defined? (Handled by set -o nounset, but good to double-check)
  if [[ -z "${target_dir}" ]]; then
    err "Safety trigger: Variable is empty. Aborting."
    exit 1
  fi

  # Check 2: Length Check
  # We check the length of the string (#variable).
  # If it is less than 5 chars, we refuse to run rm -rf.
  # This prevents disasters like: rm -rf /  or  rm -rf /usr
  if [[ "${#target_dir}" -lt 5 ]]; then
    err "Safety trigger: Path '${target_dir}' is too short or empty. Aborting delete."
    exit 1
  fi

  # Check 3: Reality Check
  # Does the directory actually exist?
  if [[ ! -d "${target_dir}" ]]; then
     log "Directory '${target_dir}' does not exist. Nothing to do."
     return 0
  fi

  # --- EXECUTION ---
  # Only runs if all checks pass
  rm -rf "${target_dir}"
  log "✅ Successfully deleted '${target_dir}'."
}

# 4. MAIN
main() {
  # Scenario A: Safe Deletion
  # Length is > 5 characters, so this is allowed.
  local temp_files="./temp_cache_files"

  # Create it first so we have something to delete
  mkdir -p "${temp_files}"

  # Run the cleanup
  safe_cleanup "${temp_files}"

  # Scenario B: Unsafe Deletion (Simulation)
  # Uncommenting the lines below would trigger the safety block and exit 1
  # local root_path="/"
  # log "Attempting to delete root..."
  # safe_cleanup "${root_path}"
}

main "$@"
