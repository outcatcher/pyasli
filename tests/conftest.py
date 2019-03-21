import os

import pytest

from pyasli.browser import BrowserSession


def in_ci():
    """Check if test is running in gitlab-ci"""
    return os.getenv("CI_JOB_NAME") is not None


@pytest.fixture(scope="module")
def browser():
    browser = browser_instance()
    browser.base_url = "https://the-internet.herokuapp.com/"
    browser.open("/broken_images")
    return browser


def browser_instance(browser: str = "chrome") -> BrowserSession:
    """Init browser session instance"""
    instance = BrowserSession(browser)
    if in_ci():  # configure remote for CI
        _brw = os.environ.get("BROWSER")
        _host = os.environ.get("HOST")
        instance.setup_browser(_brw.lower(), remote=True, command_executor=f"http://{_host}:4444/wd/hub")
    else:
        instance.options.headless = True
    return instance
