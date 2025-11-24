import os
import time


def find_old_large_files(root_dir):
    # Constants
    SIZE_LIMIT = 100 * 1024 * 1024  # 100 MB in bytes
    AGE_LIMIT_DAYS = 30
    now = time.time()
    cutoff_time = now - (AGE_LIMIT_DAYS * 86400)  # 86400 seconds in a day

    for dirpath, _, filenames in os.walk(root_dir):
        for name in filenames:
            file_path = os.path.join(dirpath, name)

            try:
                # Get file stats
                file_stats = os.stat(file_path)

                # Check size and modification time
                if (
                    file_stats.st_size > SIZE_LIMIT
                    and file_stats.st_mtime < cutoff_time
                ):
                    print(
                        f"Found: {file_path} | Size: {file_stats.st_size / 1024 / 1024:.2f}MB"
                    )
                    # os.remove(file_path) # Uncomment to delete
            except OSError as e:
                print(f"Could not access {file_path}: {e}")


# Example Usage
# find_old_large_files('/var/tmp')
