import concurrent.futures
import logging
import random
import time
from dataclasses import dataclass
from typing import Iterator, List, Optional

# Configure Structured Logging (JSON-like format preferred in production)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [worker_id:%(threadName)s] - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Standardized return object for consistent data handling."""

    file_id: str
    status: str
    duration_ms: float
    error: Optional[str] = None


def process_log_safe(log_file: str) -> ProcessingResult:
    """
    Wraps the logic in a defensive shell.
    Simulates work with jitter and random failures to test resilience.
    """
    start_time = time.time()
    try:
        # SRE Best Practice: Add "Jitter" to sleep to prevent thundering herds
        # if this were a network call.
        time.sleep(random.uniform(0.5, 1.5))

        # Simulate a random failure
        if random.random() < 0.1:
            raise ConnectionError("Simulated network flake")

        duration = (time.time() - start_time) * 1000
        return ProcessingResult(
            file_id=log_file, status="SUCCESS", duration_ms=duration
        )

    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(f"Failed to process {log_file}: {e}")
        return ProcessingResult(
            file_id=log_file, status="FAILURE", duration_ms=duration, error=str(e)
        )


def run_batch_jobs(
    file_list: List[str], max_workers: int = 10, timeout_per_job: int = 5
) -> Iterator[ProcessingResult]:
    """
    Generates results as they complete to save memory.
    """
    # SRE Best Practice: Context Manager for resource cleanup
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit dictionary maps {Future: input_arg} for error tracking
        future_to_file = {executor.submit(process_log_safe, f): f for f in file_list}

        logger.info(
            f"Batch started with {len(file_list)} files and {max_workers} workers."
        )

        try:
            # SRE Best Practice: Process results as they arrive (Streaming)
            for future in concurrent.futures.as_completed(future_to_file):
                log_file = future_to_file[future]
                try:
                    # Always enforce a timeout on .result()
                    yield future.result(timeout=timeout_per_job)
                except concurrent.futures.TimeoutError:
                    logger.error(f"Job {log_file} timed out.")
                    yield ProcessingResult(log_file, "TIMEOUT", 0.0, "TimeoutError")
                except Exception as exc:
                    # This catches unhandled exceptions in the framework itself
                    logger.critical(f"Critical worker failure for {log_file}: {exc}")

        except KeyboardInterrupt:
            # SRE Best Practice: Graceful Shutdown
            logger.warning("Received kill signal. Shutting down executor...")
            executor.shutdown(wait=False, cancel_futures=True)
            raise


# Example Usage
if __name__ == "__main__":
    files = [f"log_{i}.txt" for i in range(20)]

    # Streaming processing: We handle items one by one rather than loading a giant list
    success_count = 0
    for result in run_batch_jobs(files):
        if result.status == "SUCCESS":
            success_count += 1
            # In real life, we might emit a metric here: metrics.increment("log_processed")

    logger.info(f"Batch completed. Success rate: {success_count}/{len(files)}")
