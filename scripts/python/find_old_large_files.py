import os
import time


def find_and_clean_files(root_dir, size_limit_mb=100, age_limit_days=30, dry_run=True):
    """
    Scans a directory for old, large files.

    Args:
        root_dir (str): The starting path to scan.
        size_limit_mb (int): Minimum size in MB to qualify for deletion.
        age_limit_days (int): Minimum age (days since modification) to qualify.
        dry_run (bool): If True, only prints what would happen. If False, DELETES files.
    """

    # SRE Best Practice: Input Validation
    if not os.path.exists(root_dir):
        print(f"Error: Directory '{root_dir}' not found.")
        return

    # Convert human-readable inputs to system logic (Bytes and Seconds)
    limit_bytes = size_limit_mb * 1024 * 1024
    limit_seconds = age_limit_days * 86400
    now = time.time()

    print(f"--- Starting Scan: {root_dir} ---")
    print(f"Criteria: > {size_limit_mb}MB and > {age_limit_days} days old")
    print(f"Mode: {'DRY RUN (Safe)' if dry_run else 'LIVE (Destructive)'}")
    print("-" * 40)

    for dirpath, _, filenames in os.walk(root_dir):
        for name in filenames:
            file_path = os.path.join(dirpath, name)

            # SRE Best Practice: Symlink Safety
            # os.walk returns symlinks in 'filenames'. If we run os.stat() on a symlink,
            # it follows the link to the *target*. We do NOT want to delete a system file
            # just because a symlink in /tmp points to it.
            if os.path.islink(file_path):
                continue

            try:
                # os.stat performs a single system call to get both size and time.
                # This is more efficient than calling os.path.getsize() AND os.path.getmtime()
                stats = os.stat(file_path)

                # Logic: File is Large AND File is Old
                if (stats.st_size > limit_bytes) and (
                    stats.st_mtime < (now - limit_seconds)
                ):
                    size_mb = stats.st_size / (1024 * 1024)
                    days_old = (now - stats.st_mtime) / 86400

                    if dry_run:
                        print(
                            f"[WOULD DELETE] {file_path} | {size_mb:.2f} MB | {days_old:.1f} days old"
                        )
                    else:
                        os.remove(file_path)
                        print(f"[DELETED] {file_path}")

            except PermissionError:
                # Specific catching allows us to ignore "Access Denied" without stopping the script
                print(f"[SKIP] Permission denied: {file_path}")
            except OSError as e:
                # Catch-all for other IO errors (disk corruption, file vanished during scan)
                print(f"[ERROR] accessing {file_path}: {e}")


# --- Example Usage ---
if __name__ == "__main__":
    # SRE Tip: Default to dry_run=True to prevent accidents during testing
    find_and_clean_files(
        root_dir="/var/log", size_limit_mb=50, age_limit_days=7, dry_run=True
    )
