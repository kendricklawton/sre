import urllib.error
import urllib.request


def check_service_health(urls):
    status_report = {}

    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                # FIX: We use the variable 'response' to get the actual code.
                # This satisfies the linter and adds logging detail.
                code = response.getcode()
                status_report[url] = f"UP (Status: {code})"

        except urllib.error.HTTPError as e:
            status_report[url] = f"DOWN (Status: {e.code})"

        except urllib.error.URLError as e:
            # Converting reason to string to avoid importing socket module
            status_report[url] = f"DOWN (Reason: {str(e.reason)})"

        except Exception as e:
            status_report[url] = f"DOWN (Error: {e})"

    return status_report
