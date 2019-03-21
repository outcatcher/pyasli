import pytest

from tests.conftest import browser_instance


@pytest.fixture
def browser():
    browser = browser_instance()
    browser.open("http://the-internet.herokuapp.com/disappearing_elements")
    return browser
