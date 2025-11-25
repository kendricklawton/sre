import os
import re
from collections import Counter
from typing import List, Tuple


def find_top_error_ips(
    logfile_path: str, target_status_code: int = 500
) -> List[Tuple[str, int]]:
    """
    Parses a web server log file to find the top IPs generating specific error codes.

    Args:
        logfile_path (str): Path to the log file.
        target_status_code (int): The HTTP status code to filter for (default: 500).

    Returns:
        List[Tuple[str, int]]: Top 5 IPs and their count, e.g., [('192.168.1.1', 42), ...]
    """

    # SRE Best Practice: Input Validation
    if not os.path.exists(logfile_path):
        print(f"Error: File {logfile_path} not found.")
        return []

    ip_counter = Counter()

    # OPTIMIZATION: Compile regex once, outside the loop.
    # We changed the specific '500' to a generic '\d{3}' (any 3 digits).
    # This decouples extraction from logic. We extract EVERYTHING, filter later.
    log_pattern = re.compile(
        r"""
        ^                   # Start of line
        (?P<ip>\S+)         # Capture IP (Non-whitespace characters)
        \s                  # Separator
        .*?                 # Non-greedy match for user/date fields
        ".*?"               # Skip the HTTP request string (e.g. "GET /index.html")
        \s+                 # Separator
        (?P<status>\d{3})   # Capture ANY 3-digit status code
        """,
        re.VERBOSE,
    )

    try:
        # explicit encoding prevents crashes on weird characters in logs
        with open(logfile_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = log_pattern.search(line)
                if match:
                    # Extract data
                    captured_ip = match.group("ip")
                    captured_status = int(match.group("status"))

                    # LOGIC: Check if this is the error we care about
                    if captured_status == target_status_code:
                        ip_counter[captured_ip] += 1

        # Return top 5 most frequent offenders
        return ip_counter.most_common(5)

    except Exception as e:
        # Catch permission errors or disk read errors
        print(f"An error occurred reading the log: {e}")
        return []


# --- Example Usage ---
if __name__ == "__main__":
    # You can now use the same function for different errors without changing code
    print("Top 500 Errors:")
    print(find_top_error_ips("/var/log/nginx/access.log", target_status_code=500))

    print("\nTop 404 Errors:")
    print(find_top_error_ips("/var/log/nginx/access.log", target_status_code=404))
