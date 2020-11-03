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


def _save_screenshot(data: bytes) -> str:
    os.makedirs("./logs", exist_ok=True)
    path = os.path.abspath(f"./logs/{uuid.uuid4()}.png")
    with open(path, "wb+") as out:
        out.write(data)
    return path


class Screenshotable(abc.ABC):
    """Object instance provide screenshot functionality"""

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
        if not hasattr(instance, 'capture_screenshot'):
            warnings.warn(f'`capture_screenshot` method is missing for {instance}.'
                          'No screenshot can be captured')
            raise sc_e
        screenshot = instance.capture_screenshot()
        LOGGER.exception("Screenshot captured on failure: %s", _save_screenshot(screenshot))
        raise sc_e
