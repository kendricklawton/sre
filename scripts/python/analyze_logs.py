import argparse
import collections
import sys


def analyze_logs(file_path, target_status):
    """
    Reads a log file and counts occurrences of a specific status code per IP.
    """
    ip_counter = collections.Counter()

    try:
        with open(file_path, "r") as f:
            for line in f:
                parts = line.split()

                # Ensure we have enough parts (Timestamp, IP, Method, Status...)
                if len(parts) > 3:
                    ip = parts[1]  # Adjust index if needed
                    status = parts[3]  # Adjust index if needed

                    # Compare against the target_status argument
                    if status == target_status:
                        ip_counter[ip] += 1

        # Output results
        print(f"--- Analyzing '{file_path}' for Status {target_status} ---")
        top_5 = ip_counter.most_common(5)

        if not top_5:
            print(f"No IPs found with status {target_status}.")
        else:
            print("Top 5 IPs:")
            for ip, count in top_5:
                print(f"{ip}: {count}")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)  # Exit with an error code
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


# --- ARGPARSE SETUP ---
if __name__ == "__main__":
    # 1. Initialize the parser
    parser = argparse.ArgumentParser(
        description="Analyze server log files for specific HTTP status codes."
    )

    # 2. Add a 'Positional' argument (Required)
    # The user MUST provide the filename.
    parser.add_argument(
        "filename", help="The path to the log file you want to analyze."
    )

    # 3. Add an 'Optional' argument (Flag)
    # The user CAN provide this. If not, it defaults to "500".
    parser.add_argument(
        "--status",
        "-s",
        default="500",
        help="The HTTP status code to search for (default: 500).",
    )

    # 4. Parse the arguments
    args = parser.parse_args()

    # 5. Run the logic using the parsed arguments
    analyze_logs(args.filename, args.status)
