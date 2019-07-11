import pytest

from tests.conftest import browser_instance


@pytest.fixture(scope="session")
def browser(base_url):
    with browser_instance() as browser:
        browser.base_url = base_url
        browser.open("/disappearing_elements")
        yield browser
