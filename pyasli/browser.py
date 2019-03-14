from __future__ import annotations

import atexit
from typing import Dict, Type

import wrapt
from selenium.webdriver import Chrome, ChromeOptions, Firefox, FirefoxOptions, Ie, IeOptions, Remote

from pyasli.elements import CssSelectorOrBy, Element, ElementCollection, SearchableWithElements
from pyasli.searchable import Wrapped

_BROWSER_MAPPING: Dict[str, Type[Remote]] = {
    "chrome": Chrome,
    "ie": Ie,
    "firefox": Firefox,
    "remote": Remote,
}

_OPTIONS_MAPPING = {
    "chrome": ChromeOptions,
    "ie": IeOptions,
    "firefox": FirefoxOptions,
}


# noinspection PyProtectedMember
@wrapt.decorator
def requires_browser(wrapped, instance: BrowserSession = None, args=(), kwargs=None):
    """Decorator forcing instance to has webdriver instance before running method"""
    if instance._web_driver is None:
        browser_cls = _BROWSER_MAPPING[instance._browser]
        instance._web_driver = browser_cls(options=instance._options, **instance._other_options)
    return wrapped(args, kwargs)


class BrowserSession(SearchableWithElements):
    """Class containing single webdriver instance and all browser operations"""

    _web_driver: Remote = None
    _browser: str = None
    _options = None
    _other_options: dict = None

    def __init__(self, browser="chrome", remote=False, options=None, **kwargs):
        """Init new browser session.
        Arguments for creating webdriver instance other than ``options`` should be passed to kwargs
        """
        super().__init__(None)
        self.__cached__ = browser
        self.configure_browser(browser, remote, options, **kwargs)
        atexit.register(self.close_all_windows)

    def _search(self) -> Wrapped:
        return self.__cached__

    def configure_browser(self, browser="chrome", remote=False, options=None, **kwargs):
        """Configure browser for session"""
        if browser not in _BROWSER_MAPPING:
            raise TypeError(f"Browser `{browser}`` is not supported. Select one of {_BROWSER_MAPPING.keys()}")

        if remote:
            self._browser = "remote"
            # if no options given or already set, should set browser
            # empty set of browser Options for desired browser
            self._options = options or self._options or _OPTIONS_MAPPING[browser]()
        else:
            self._browser = browser or self._browser
            self._options = options or self._options
        self._other_options = kwargs or self._other_options

    @requires_browser
    def open(self, url: str):
        """Open given URL"""
        self._web_driver.get(url)

    @requires_browser
    def element(self, css_or_locator: CssSelectorOrBy) -> Element:
        """Find single element by locator (css selector by default)"""
        return super().element(css_or_locator)

    @requires_browser
    def elements(self, css_or_locator: CssSelectorOrBy) -> ElementCollection:
        """Find single element by locator (css selector by default)"""
        return super().elements(css_or_locator)

    @requires_browser
    def add_cookie(self, cookie_dict: dict):
        """Add cookies to cookie storage"""
        self._web_driver.add_cookie(cookie_dict)

    @requires_browser
    def close_window(self):
        """Close current browser window"""
        self._web_driver.close()

    @requires_browser
    def close_all_windows(self):
        """Close all browser windows"""
        self._web_driver.quit()
