"""Basic browser session tests"""

import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Firefox, FirefoxOptions
from urllib3.exceptions import MaxRetryError

from pyasli.browser import BrowserSession, NoBrowserException


def test_open(browser):
    """No exceptions is enough here"""
    browser = BrowserSession(headless=True)
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
    browser = BrowserSession(headless=True)
    browser.element("html")


def test_firefox():
    browser = BrowserSession("firefox", headless=True)
    browser.open("http://the-internet.herokuapp.com/disappearing_elements")
    browser.element("html").get_actual()


def test_remote():
    browser = BrowserSession("firefox", remote=True, headless=True)
    assert not isinstance(browser.get_actual(), Firefox)
    assert isinstance(browser._options, FirefoxOptions)


def test_url_check(browser):
    """No exceptions is enough here"""
    browser = BrowserSession(headless=True)
    browser.open("http://the-internet.herokuapp.com/disappearing_elements")
    assert browser.url == "http://the-internet.herokuapp.com/disappearing_elements"
