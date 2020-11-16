import os

import pytest

from pyasli.conditions import visible


def test_negative_wait(browser, log_dir):
    with pytest.raises(TimeoutError):
        browser.element("div#id").assure(visible, 0.1)
    _check_screenshot(log_dir)


def test_negative_wait_assert(browser, log_dir):
    with pytest.raises(AssertionError):
        browser.element("div#id").should_be(visible, 0.1)
    _check_screenshot(log_dir)


@pytest.fixture
def log_dir(random_string):
    return f"./{random_string}"


def _check_screenshot(path):
    for _, _, files in os.walk(path):
        assert len(files) == 1
        screenshot = files[0]
        assert screenshot.endswith(".png")
