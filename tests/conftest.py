import os
import random
import string
import time

import pytest
import requests

from pyasli.browsers import BrowserSession
from pyasli.elements.elements import Element


@pytest.fixture(scope="session")
def base_url():
    """Return site test server base URL"""
    if target_port := os.getenv("LOCAL_PORT"):
        return f"http://localhost:{target_port}"

    return "https://the-internet.herokuapp.com"


@pytest.fixture(scope="module")
def browser(base_url):
    brw = browser_instance(base_url=base_url)
    yield brw
    brw.close_all_windows()


def in_ci():
    """Check if test is running in travis"""
    return os.getenv("CI") is not None


skip_if_ci = pytest.mark.skipif(in_ci(), reason="Running in CI")
skip_if_not_ci = pytest.mark.skipif(not in_ci(), reason="Running not in CI")


@pytest.fixture
def single_time_browser(base_url):
    brw = browser_instance(base_url=base_url)
    brw.open("/broken_images")
    yield brw
    brw.close_all_windows()


HUB_URL = "http://{host}:4444/wd/hub"


def _wait_hub_available(host, timeout=5):
    end_time = time.monotonic() + timeout
    while time.monotonic() < end_time:
        try:
            requests.head(HUB_URL.format(host=host))
            return
        except requests.exceptions.ConnectionError:
            time.sleep(0.2)
    raise TimeoutError(f"Hub at {HUB_URL.format(host=host)} is not available after {timeout} seconds")


def browser_instance(browser: str = "chrome", base_url=None) -> BrowserSession:
    """Init browser session instance"""
    instance = BrowserSession(browser, base_url)
    if in_ci():  # configure remote for CI
        _brw = os.environ.get("BROWSER")
        _host = os.environ.get("HOST")
        _wait_hub_available(_host)
        instance.setup_browser(_brw.lower(), remote=True, command_executor=HUB_URL.format(host=_host))
    else:
        instance.options.headless = True
    return instance


def tags(*applied_tags: str):
    """Let use :fnc:`pytest.mark` in way:

        ``@tag("smoke")...`` or ``@tags("smoke", "draft")``
    """

    def _marks(wrapped):
        marks = pytest.mark
        for _tag in applied_tags:
            actual_mark = getattr(marks, _tag)
            wrapped = actual_mark(wrapped)
        return wrapped

    return _marks


tag = tags


class TimeoutCondition:
    """Simulating timeout becoming True after timeout"""

    def __init__(self, timeout, results=(False, True)):
        self.timeout = timeout
        self.results_before, self.results_after = results[:2]
        self.end_time = None

    def __call__(self):
        if self.end_time is None:
            self.end_time = time.time() + self.timeout
        if time.time() > self.end_time:
            return self.results_after
        return self.results_before


class ElementMock(Element):
    """Element mocking checks"""

    def __init__(self):
        self.timeout = 0.01
        self._locator = None
        self._visible = TimeoutCondition(self.timeout)
        self._text = TimeoutCondition(self.timeout, ("before", "after"))
        self._exists = TimeoutCondition(self.timeout)
        self._enabled = TimeoutCondition(self.timeout)
        self._refresh_state()

    def _refresh_state(self):
        self._exists()
        self._visible()
        self._enabled()
        self._text()

    def _search(self):
        return None

    @property
    def visible(self):
        return self._visible()

    @property
    def text(self):
        return self._text()

    @property
    def exists(self):
        return self._exists()

    @property
    def enabled(self):
        return self._enabled()


@pytest.fixture
def element() -> ElementMock:
    # noinspection PyTypeChecker
    return ElementMock()


@pytest.fixture
def random_string():
    """Generate 10 char random string"""
    return "".join(random.choice(string.ascii_letters) for _ in range(10))
