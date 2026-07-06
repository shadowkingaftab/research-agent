import time


def retry(func, *args, retries=3, delay=2, **kwargs):

    last_error = None

    for attempt in range(retries):

        try:
            return func(*args, **kwargs)

        except Exception as e:

            last_error = e

            print(f"Retry {attempt + 1}/{retries}: {e}")

            time.sleep(delay)

    raise last_error