"""Shared browser, safe to use with pytest-xdist"""
import logging

from .browser_session import BrowserSession

LOGGER = logging.getLogger(__name__)

browser = BrowserSession()  # pylint: disable=invalid-name


class _BrowserState:
    """Static container for browser state"""

    # only browser_name, lol
    browser_name = "chrome"  # please, don't change me directly

    def __new__(cls):
        raise NotImplementedError


def set_browser(browser_name: str):
    """Set shared browser. More precise configuration can be reached with `browser.setup_browser`"""
    LOGGER.debug('Set shared browser to %s', browser_name)
    if browser_name != _BrowserState.browser_name:
        browser.close_all_windows()
        _BrowserState.browser_name = browser_name
    browser.setup_browser(browser_name)
