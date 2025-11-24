import re
from collections import Counter


def find_top_error_ips(logfile_path):
    ip_counter = Counter()

    # Note: We filter for '500' directly in regex here.
    # If you need other codes later, change '500' back to '\d{3}'
    log_pattern = re.compile(
        r"""
        ^                   # Start of line
        (?P<ip>\S+)         # Capture IP (IPv4 or IPv6)
        \s                  # Separator
        .*?                 # Skip identd/user/date
        ".*?"               # Skip the request string
        \s+                 # Separator
        (?P<status>500)     # Capture specific Status Code
    """,
        re.VERBOSE,
    )

    try:
        with open(logfile_path, "r") as f:
            for line in f:
                match = log_pattern.search(line)
                if match:
                    # No need to check "if status == 500" because the regex did it
                    ip_counter[match.group("ip")] += 1

        return ip_counter.most_common(5)
    except FileNotFoundError:
        return []
