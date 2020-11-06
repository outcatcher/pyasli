"""Basic browser session tests"""
import os

import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome, ChromeOptions, Firefox, FirefoxOptions, Remote
from webdriver_manager.firefox import GeckoDriverManager

from pyasli.browsers.browser_session import NoBrowserException, URL
from tests.conftest import browser_instance, skip_if_ci, skip_if_not_ci, tags


def test_open(base_url, single_time_browser):
    """No exceptions is enough here"""
    single_time_browser.open(f"{base_url}/disappearing_elements")
    single_time_browser.element("html").get_actual()


def test_close_all(single_time_browser):
    """Check that all browser windows are closed"""
    single_time_browser.close_all_windows()
    with pytest.raises(NoBrowserException):
        single_time_browser.element("html").get_actual()


def test_close_all_not_started():
    brw = browser_instance()
    brw.close_all_windows()


def test_closed_with_context():
    with browser_instance() as brw:
        brw.close_all_windows()


def test_close_all_reopen(single_time_browser):
    single_time_browser.close_all_windows()
    single_time_browser.open("/")


def test_close_single(single_time_browser):
    """Check that single browser window is closed"""
    single_time_browser.close_window()
    with pytest.raises(WebDriverException):
        single_time_browser.element("html").get_actual()


def test_no_open_page():
    with browser_instance() as browser:
        el = browser.element("html")
        with pytest.raises(NoBrowserException):
            el.get_actual()


@tags("chrome")
@skip_if_ci
def test_chrome(base_url):
    with browser_instance("chrome", base_url) as browser:
        browser.open("/disappearing_elements")
        browser.element("html").get_actual()


@tags("firefox")
@skip_if_ci
def test_firefox(base_url):
    with browser_instance("firefox", base_url) as browser:
        browser.open("/disappearing_elements")
        browser.element("html").get_actual()
        browser.close_all_windows()


def test_lazy_init():
    browser = browser_instance()
    assert browser._actual is None


@skip_if_not_ci
def test_remote(base_url):
    with browser_instance() as browser:
        host = os.environ.get('HOST')
        browser.setup_browser("chrome", remote=True, command_executor=f"http://{host}:4444/wd/hub")
        browser.open(base_url)
        assert not isinstance(browser._actual, Chrome)
        assert isinstance(browser._actual, Remote)
        assert isinstance(browser.options, ChromeOptions)


def test_url_check(single_time_browser, base_url):
    """No exceptions is enough here"""
    with browser_instance(base_url=base_url) as browser:
        url = "/disappearing_elements"
        browser.open(url)
        assert browser.url == f"{base_url}{url}"


def test_url_ne_check(single_time_browser, base_url):
    """No exceptions is enough here"""
    with browser_instance(base_url=base_url) as browser:
        url = "/disappearing_elements"
        browser.open(url)
        assert browser.url != f"{base_url}/.../{url}"


@tags("firefox")
@skip_if_ci
def test_set_driver(base_url):
    with browser_instance() as browser:
        options = FirefoxOptions()
        options.headless = True
        browser.set_driver(Firefox(options=options, executable_path=GeckoDriverManager().install()))
        assert isinstance(browser._actual, Firefox)  # not lazy!
        browser.open(base_url)


@tags("firefox")
@skip_if_ci
def test_replace_driver(base_url):
    with browser_instance() as browser:
        browser.open(base_url)
        options = FirefoxOptions()
        options.headless = True
        browser.set_driver(Firefox(options=options, executable_path=GeckoDriverManager().install()))
        assert isinstance(browser._actual, Firefox)  # not lazy!
        browser.open(base_url)


def test_no_base_url():
    actual = "dfsbhjhjdgflslidgfsn"
    url = URL(actual, None)
    assert url.base_url is None
    assert url.url == actual
    assert url == actual
