import os
import shutil

import pytest


@pytest.mark.xfail(raises=TimeoutError)
def test_negative_wait(browser):
    browser.element("div#id").assure.visible(0.5)


@pytest.mark.xfail(raises=AssertionError)
def test_negative_wait_assert(browser):
    browser.element("div#id").should_be.visible(0.5)


@pytest.fixture
def cleanup():
    lgs = "./logs"
    if not os.path.exists(lgs):
        return
    shutil.rmtree(lgs)


def test_negative_wait_screenshot(browser, cleanup):
    try:
        browser.element("div#id").assure.visible(0.5)
    except TimeoutError:
        pass
    for roots, dirs, files in os.walk("./logs"):
        assert len(files) == 1
        assert files[0].endswith(".png")
