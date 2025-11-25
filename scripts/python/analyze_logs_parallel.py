import json
import os
from multiprocessing import Pool, cpu_count


def process_chunk(args):
    """
    Worker function: Processes a specific byte range of the file.
    """
    filepath, start_byte, end_byte, target_error = args

    local_count = 0
    local_first = None
    local_last = None

    with open(filepath, "r") as f:
        # 1. Jump to the assigned starting position
        f.seek(start_byte)

        # 2. ALIGNMENT HANDLING (Critical SRE Logic)
        # If we aren't at the start of the file, we are likely in the middle
        # of a line. Skip the rest of that line so we start fresh.
        # The *previous* worker will handle that partial line.
        if start_byte != 0:
            f.readline()

        # 3. Process lines until we hit our end_byte
        while f.tell() < end_byte:
            line = f.readline()
            if not line:
                break  # End of file

            try:
                entry = json.loads(line)
                if entry.get("error_code") == target_error:
                    timestamp = entry.get("timestamp")
                    local_count += 1

                    if local_first is None:
                        local_first = timestamp
                    local_last = timestamp
            except json.JSONDecodeError:
                continue

    return {"count": local_count, "first": local_first, "last": local_last}


def analyze_logs_parallel(filepath, target_error="DB_TIMEOUT"):
    """
    Master function: Splits file and aggregates results.
    """
    # Get file size to calculate chunks
    file_size = os.path.getsize(filepath)
    cpu_cores = cpu_count()

    # Calculate chunk size (e.g., 100MB file / 4 cores = 25MB per core)
    chunk_size = file_size // cpu_cores

    # Prepare arguments for each worker
    chunk_args = []
    for i in range(cpu_cores):
        start = i * chunk_size
        # The last worker takes whatever is left until the end of the file
        end = file_size if i == cpu_cores - 1 else (i + 1) * chunk_size
        chunk_args.append((filepath, start, end, target_error))

    # Spin up the pool of workers
    print(f"Spawning {cpu_cores} workers to process {filepath}...")
    with Pool(cpu_cores) as pool:
        results = pool.map(process_chunk, chunk_args)

    # REDUCE STEP: Aggregate results from all workers
    total_count = 0
    global_first = None
    global_last = None

    for r in results:
        if r["count"] > 0:
            total_count += r["count"]

            # Logic to find the absolute earliest/latest across all chunks
            if global_first is None or (
                r["first"] is not None and r["first"] < global_first
            ):
                global_first = r["first"]

            if global_last is None or (
                r["last"] is not None and r["last"] > global_last
            ):
                global_last = r["last"]

    return {
        "error_code": target_error,
        "count": total_count,
        "first_seen": global_first,
        "last_seen": global_last,
    }


# Note: In Windows/Mac, multiprocessing requires this guard:
if __name__ == "__main__":
    # Create a dummy file for testing if needed
    # result = analyze_log_parallel("huge_server.log")
    # print(result)
    pass
