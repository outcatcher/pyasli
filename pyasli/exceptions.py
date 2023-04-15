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


class Screenshotable(abc.ABC):
    """Object instance provide screenshot functionality"""

    @property
    @abc.abstractmethod
    def log_path(self) -> str: ...

    @abc.abstractmethod
    def capture_screenshot(self) -> bytes: ...

    def capture_screenshot_and_save(self, prefix="") -> str:
        """Capture whole browser page screenshot and save it to log dir"""
        png_data = self.capture_screenshot()

        os.makedirs(self.log_path, exist_ok=True)
        img_path = os.path.abspath(f"{self.log_path}/{prefix}{uuid.uuid4()}.png")

        with open(img_path, "wb+") as out:
            out.write(png_data)

        return img_path


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
            img_path = instance.capture_screenshot_and_save()
            LOGGER.exception("Screenshot captured on failure: %s", img_path)
        except NoBrowserException:
            pass

        raise sc_e
