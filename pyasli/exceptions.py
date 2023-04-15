import abc
import logging
import os
import uuid
import warnings

import wrapt
from selenium.common.exceptions import WebDriverException

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.ERROR)
__STH = logging.StreamHandler()
__STH.setLevel(logging.ERROR)
LOGGER.addHandler(__STH)


class NoBrowserException(WebDriverException):
    """No operable browser is open"""


def _save_screenshot(data: bytes, dir_path="./logs") -> str:
    os.makedirs(dir_path, exist_ok=True)
    img_path = os.path.abspath(f"{dir_path}/{uuid.uuid4()}.png")
    with open(img_path, "wb+") as out:
        out.write(data)
    return img_path


class Screenshotable(abc.ABC):
    """Object instance provide screenshot functionality"""

    @property
    @abc.abstractmethod
    def log_path(self) -> str: ...

    @abc.abstractmethod
    def capture_screenshot(self) -> bytes: ...


@wrapt.decorator
def screenshot_on_fail(wrapped, instance: Screenshotable = None, args=None, kwargs=None):
    """Capture screenshot on method error

    One of the following errors handled: WebDriverException, AssertionError, TimeoutError
    """
    try:
        return wrapped(*args, **kwargs)
    except (WebDriverException, AssertionError, TimeoutError) as sc_e:
        if not hasattr(instance, "capture_screenshot"):
            warnings.warn(f"`capture_screenshot` method is missing for {instance}."
                          "No screenshot can be captured", stacklevel=2)
            raise sc_e

        try:
            img_path = _save_screenshot(instance.capture_screenshot(), instance.log_path)
            LOGGER.exception("Screenshot captured on failure: %s", img_path)
        except NoBrowserException:
            pass

        raise sc_e #
