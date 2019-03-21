import pytest

from pyasli.browser import BrowserSession


@pytest.fixture(scope="session")
def browser():
    browser = BrowserSession()
    browser.base_url = "http://the-internet.herokuapp.com"
    browser.open("/disappearing_elements")
    yield browser
    browser.close_all_windows()
