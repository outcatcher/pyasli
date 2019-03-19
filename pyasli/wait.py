"""Condition waiting"""
import os
import time
import uuid
from typing import Callable, TypeVar

T = TypeVar("T")


def _save_screenshot(data: bytes) -> str:
    os.makedirs("./logs", exist_ok=True)
    path = f"./logs/{uuid.uuid4()}.png"
    with open(path, "wb+") as out:
        out.write(data)
    return path


def wait_for(element: "Element", condition: Callable[["Element"], bool], timeout=5, exception=None):
    """Wait until condition for element is satisfied"""
    end_time = time.time() + timeout
    polling_time = 0.05
    while time.time() < end_time:
        if condition(element):
            return
        time.sleep(polling_time)
    print(f"Screenshot captured on failure: {_save_screenshot(element.browser.get_screenshot_as_png())}")
    raise exception or TimeoutError(f"Wait time has expired for condition `{condition}`")
