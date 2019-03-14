import time
from collections import Callable
from typing import TypeVar

T = TypeVar("T")


def wait_for(condition: Callable[[], bool], timeout=5):
    """Wait until condition for element is satisfied"""
    end_time = time.time() + timeout
    polling_time = 0.05
    while time.time() < end_time:
        if condition():
            return
        time.sleep(polling_time)
    raise TimeoutError(f"Wait time has expired for condition `{condition}`")
