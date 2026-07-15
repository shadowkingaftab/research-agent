import random
import time

from core.logger import logger


def retry(
    func,
    *args,
    retries=3,
    delay=2,
    backoff=2,
    **kwargs,
):

    last_error = None

    current_delay = delay

    for attempt in range(1, retries + 1):

        try:

            return func(*args, **kwargs)

        except (
            TimeoutError,
            ConnectionError,
        ) as e:

            last_error = e

            logger.log(
                f"Retry {attempt}/{retries}: {e}"
            )

            if attempt < retries:

                sleep_time = (
                    current_delay
                    + random.uniform(0, 0.5)
                )

                time.sleep(sleep_time)

                current_delay *= backoff

        except Exception:

            raise

    logger.log(
        f"Operation failed after {retries} attempts."
    )

    raise last_error