from concurrent.futures import ThreadPoolExecutor
import os

MAX_WORKERS = int(
    os.getenv("MAX_WORKERS", 8)
)

executor = ThreadPoolExecutor(
    max_workers=MAX_WORKERS
)

def submit(func, *args, **kwargs):
    return executor.submit(
        func,
        *args,
        **kwargs,
    )

def shutdown(wait=True):
    executor.shutdown(wait=wait)