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

# 2. CONFIGURATION & GLOBALS
# 'nullglob': If *.txt matches nothing, the loop won't run.
# This replaces the need for your [ ! -e "$file" ] check.
shopt -s nullglob

# 3. LOGGING
log() {
  echo "[INFO] $*" >&2
}

err() {
  echo "[ERROR] $*" >&2
}

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") --old <ext> --new <ext> [--dry-run]

Options:
  -o, --old      Old file extension (e.g., txt)
  -n, --new      New file extension (e.g., log)
  -d, --dry-run  Preview changes without renaming
  -h, --help     Show this help message
EOF
  exit 1
}

# 4. CORE LOGIC
rename_files() {
  local old_ext="$1"
  local new_ext="$2"
  local dry_run="$3"
  local count=0

  # Remove leading dots if user provided them (e.g. ".txt" -> "txt")
  old_ext="${old_ext#.}"
  new_ext="${new_ext#.}"

  log "Scanning for *.${old_ext} files..."

  for file in *."${old_ext}"; do
    # Parameter Expansion: Strip the old extension
    local base_name="${file%.${old_ext}}"
    local target_name="${base_name}.${new_ext}"

    # Conflict Check: Don't overwrite if target exists
    if [[ -e "${target_name}" ]]; then
      err "Skipping '${file}': Target '${target_name}' already exists."
      continue
    fi

    # Execution
    if [[ "${dry_run}" == "true" ]]; then
      log "[DRY-RUN] Would rename: '${file}' -> '${target_name}'"
    else
      mv --no-clobber "${file}" "${target_name}"
      log "Renamed: '${file}' -> '${target_name}'"
    fi

    ((count++))
  done

  if [[ "${count}" -eq 0 ]]; then
    log "No files found with extension .${old_ext}"
  else
    log "Job Complete. Processed ${count} files."
  fi
}

# 5. MAIN
main() {
  local old_ext=""
  local new_ext=""
  local dry_run="false"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -o|--old)
        old_ext="$2"
        shift 2
        ;;
      -n|--new)
        new_ext="$2"
        shift 2
        ;;
      -d|--dry-run)
        dry_run="true"
        shift 1
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
  if [[ -z "${old_ext}" || -z "${new_ext}" ]]; then
    err "Both --old and --new extensions are required."
    usage
  fi

  rename_files "${old_ext}" "${new_ext}" "${dry_run}"
}

main "$@"
