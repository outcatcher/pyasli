"""Basic browser session tests"""
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome, ChromeOptions, Firefox, FirefoxOptions, Remote
from urllib3.exceptions import MaxRetryError
from webdriver_manager.firefox import GeckoDriverManager

from pyasli.browser import NoBrowserException
from tests.conftest import browser_instance, in_ci


def test_open(browser):
    """No exceptions is enough here"""
    browser = browser_instance()
    browser.open("http://the-internet.herokuapp.com/disappearing_elements")
    browser.element("html").get_actual()


@pytest.mark.xfail(raises=MaxRetryError, reason="Can't connect to quited driver")
def test_close_all(browser):
    """Check that all browser windows are closed"""
    browser.close_all_windows()
    browser.element("html").get_actual()


@pytest.mark.xfail(raises=WebDriverException, reason="Can't interact with already closed browser")
def test_close_single(browser):
    """Check that single browser window is closed"""
    browser.close_window()
    browser.element("html").get_actual()


@pytest.mark.xfail(raises=NoBrowserException, reason="Can't interact with non-existing browser")
def test_missing_browser():
    browser = browser_instance()
    browser.element("html")


skip_if_ci = pytest.mark.skipif(in_ci(), reason="Running in CI")
skip_if_not_ci = pytest.mark.skipif(not in_ci(), reason="Running not in CI")


@skip_if_ci
def test_chrome():
    browser = browser_instance("chrome")
    browser.open("http://the-internet.herokuapp.com/disappearing_elements")
    browser.element("html").get_actual()


@skip_if_ci
def test_firefox():
    browser = browser_instance("firefox")
    browser.open("http://the-internet.herokuapp.com/disappearing_elements")
    browser.element("html").get_actual()


def test_lazy_init():
    browser = browser_instance()
    assert browser.get_actual() is None


@skip_if_not_ci
def test_remote():
    browser = browser_instance()
    browser.setup_browser("chrome", remote=True)
    browser.open("http://the-internet.herokuapp.com/")
    assert not isinstance(browser.get_actual(), Chrome)
    assert isinstance(browser.get_actual(), Remote)
    assert isinstance(browser.options, ChromeOptions)


def test_url_check(browser):
    """No exceptions is enough here"""
    browser.open("http://the-internet.herokuapp.com/disappearing_elements")
    assert browser.url == "http://the-internet.herokuapp.com/disappearing_elements"


@skip_if_ci
def test_set_driver():
    browser = browser_instance()
    options = FirefoxOptions()
    options.headless = True
    browser.set_driver(Firefox(options=options, executable_path=GeckoDriverManager().install()))
    assert isinstance(browser.get_actual(), Firefox)  # not lazy!
    browser.open("http://the-internet.herokuapp.com/")


@skip_if_ci
def test_replace_driver():
    browser = browser_instance()
    browser.open("http://the-internet.herokuapp.com/")
    options = FirefoxOptions()
    options.headless = True
    browser.set_driver(Firefox(options=options, executable_path=GeckoDriverManager().install()))
    assert isinstance(browser.get_actual(), Firefox)  # not lazy!
    browser.open("http://the-internet.herokuapp.com/")
