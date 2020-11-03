import os
import shutil

import pytest

from pyasli.conditions import visible


def test_negative_wait(browser, cleanup):
    with pytest.raises(TimeoutError):
        browser.element("div#id").assure(visible, 0.1)
    _check_screenshot()


def test_negative_wait_assert(browser, cleanup):
    with pytest.raises(AssertionError):
        browser.element("div#id").should_be(visible, 0.1)
    _check_screenshot()


@pytest.fixture
def cleanup():
    yield
    lgs = "./logs"
    if os.path.exists(lgs):
        shutil.rmtree(lgs)


def _check_screenshot():
    for _, _, files in os.walk("./logs"):
        assert len(files) == 1
        screenshot = files[0]
        assert screenshot.endswith(".png")
