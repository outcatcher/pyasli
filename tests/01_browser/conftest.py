import pytest

from pyasli.browser import BrowserSession


@pytest.fixture
def browser():
    browser = BrowserSession(headless=True)
    browser.open("http://the-internet.herokuapp.com/disappearing_elements")
    return browser
