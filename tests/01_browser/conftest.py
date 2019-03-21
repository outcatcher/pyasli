import pytest

from pyasli.browser import BrowserSession


@pytest.fixture
def browser():
    browser = BrowserSession()
    browser.open("http://the-internet.herokuapp.com/disappearing_elements")
    return browser
