import pytest

from tests.conftest import browser_instance


@pytest.fixture(scope="session")
def browser():
    browser = browser_instance()
    browser.base_url = "http://the-internet.herokuapp.com"
    browser.open("/disappearing_elements")
    yield browser
    browser.close_all_windows()
