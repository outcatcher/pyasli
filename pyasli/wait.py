"""Condition waiting"""
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def wait_for(element: T, condition: Callable[[T], bool], timeout=5, exception=None):
    """Wait until condition for element is satisfied"""
    end_time = time.time() + timeout
    polling_time = 0.05
    while time.time() < end_time:
        if condition(element):
            return
        time.sleep(polling_time)
    message = f"Wait time has expired for condition `{condition.__name__}`"
    raise exception or TimeoutError(message)
