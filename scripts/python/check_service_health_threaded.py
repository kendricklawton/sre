from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def check_single_url(url):
    """
    Helper function to check a single URL.
    Returns a tuple: (url, status_string)
    """
    timeout_sec = 3
    try:
        response = requests.get(url, timeout=timeout_sec)
        response.raise_for_status()
        return url, f"UP (Status: {response.status_code})"

    except requests.exceptions.HTTPError as e:
        return url, f"DOWN (HTTP Error: {e.response.status_code})"
    except requests.exceptions.Timeout:
        return url, "DOWN (Timeout)"
    except requests.exceptions.ConnectionError:
        return url, "DOWN (Connection Failed)"
    except requests.exceptions.RequestException as e:
        return url, f"DOWN (Error: {e})"


def check_service_health_threaded(urls):
    status_report = {}

    # WORKER POOL:
    # 10-20 threads is usually a sweet spot for network requests.
    # Too many threads (e.g., 500) creates overhead from 'context switching'.
    MAX_WORKERS = 10

    print(f"Checking {len(urls)} URLs with {MAX_WORKERS} threads...")

    # Context manager handles creating and destroying threads automatically
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit tasks to the pool
        # future_to_url acts as a tracker for our running threads
        future_to_url = {executor.submit(check_single_url, url): url for url in urls}

        # Process results as they complete (as_completed yields futures as they finish)
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                # The result is the return value of check_single_url
                checked_url, status = future.result()
                status_report[checked_url] = status
            except Exception as exc:
                # Safety net if the thread itself crashes hard
                status_report[url] = f"CRITICAL SCRIPT ERROR: {exc}"

    return status_report


# --- Example Usage ---
if __name__ == "__main__":
    # Simulating a list of 20 urls for the demo
    my_urls = [
        "https://www.google.com",
        "https://www.github.com",
        "https://www.python.org",
    ] * 7

    report = check_service_health_threaded(my_urls)

    # Print first 5 just to see
    for k, v in list(report.items())[:5]:
        print(f"{k}: {v}")
