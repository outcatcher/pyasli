import os

import pytest
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import HTTPError

from pyasli.browsers import browser, set_browser
from tests.conftest import in_ci, skip_if_ci, skip_if_not_ci


@pytest.fixture
def patch_browser():  # prepare driver for CI
    if in_ci():  # configure remote for CI
        _brw = os.getenv("BROWSER")
        _host = os.getenv("HOST")
        browser.setup_browser(_brw.lower(), remote=True, command_executor=f"http://{_host}:4444/wd/hub")
    else:
        browser.options.headless = True


def test_base(patch_browser, base_url):
    browser.open(base_url)


@pytest.fixture
def revert_changes():
    """Reset browser to default one"""
    yield
    set_browser("chrome")


@skip_if_ci
def test_set_same(patch_browser, base_url):
    set_browser(browser.browser_name)
    browser.open(base_url)
    webdriver_session_id = browser.get_actual().session_id
    set_browser(browser.browser_name)
    assert webdriver_session_id == browser.get_actual().session_id


def test_set_browser(patch_browser, revert_changes):
    set_browser("firefox")
    assert browser.browser_name == "firefox"


@skip_if_ci
def test_set_running_browser(base_url, patch_browser, revert_changes):
    browser.open(base_url)
    wrapped_driver = browser.get_actual()
    set_browser("firefox")
    assert browser.browser_name == "firefox"
    with pytest.raises(HTTPError):  # browser session is dead
        wrapped_driver.get(base_url)


@skip_if_not_ci
def test_set_running_browser(base_url, patch_browser, revert_changes):
    browser.open(base_url)
    wrapped_driver = browser.get_actual()
    set_browser("firefox")
    assert browser.browser_name == "firefox"
    with pytest.raises(WebDriverException):  # browser session is dead
        wrapped_driver.get(base_url)
