import pytest

from tests.conftest import browser_instance


@pytest.fixture(scope="session")
def browser(base_url):
    browser = browser_instance()
    browser.base_url = base_url
    browser.open("/disappearing_elements")
    yield browser
    browser.close_all_windows()
