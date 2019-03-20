"""Browser management"""

from __future__ import annotations

import atexit
import re
from functools import partial
from typing import Dict, NamedTuple, Type

import wrapt
from selenium.webdriver import Chrome, ChromeOptions, Firefox, FirefoxOptions, Ie, IeOptions, Remote
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager

from pyasli.bys import CssSelectorOrBy
from pyasli.elements import BROWSER, Element, ElementCollection, Searchable, Wrapped

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

_MANAGER_MAPPING = {
    "chrome": ChromeDriverManager,
    "ie": IEDriverManager,
    "firefox": GeckoDriverManager,
}


class NoBrowserException(Exception):
    """No operatable browser is open"""


@wrapt.decorator
def _check_browser(wrapped, instance: BrowserSession = None, args=(), kwargs=None):
    if instance.__cached__ is None:
        raise NoBrowserException("You should open some page before doing anything")
    return wrapped(*args, **kwargs)


_FULL_URL_RE = re.compile(r"http(s)?://.+")


class BrowserSession(Searchable):
    """Class containing single webdriver instance and all browser operations"""

    __cached__: Remote = None
    _browser: str = None
    _options = None
    _other_options: dict = None

    def __init__(self, browser="chrome", remote=False, headless=False, options=None, **kwargs):
        """Init new browser session.
        Arguments for creating webdriver instance other than ``options`` should be passed to kwargs
        """
        # noinspection PyTypeChecker
        super().__init__(BROWSER)
        self.configure_browser(browser, remote, headless, options, **kwargs)
        atexit.register(self.close_all_windows)

    def _search(self) -> Wrapped:
        return self.__cached__

    def __init_browser(self):
        """Init browser if it is missing"""
        if self.__cached__ is not None:
            return
        browser_cls = _BROWSER_MAPPING[self._browser]
        driver_partial = partial(browser_cls, options=self._options, **self._other_options)
        if browser_cls == Remote:
            self.__cached__ = driver_partial()  # no need to install driver
            return
        manager_cls = _MANAGER_MAPPING[self._browser]
        if browser_cls == Firefox:
            self.__cached__ = driver_partial(executable_path=manager_cls().install())
        else:
            self.__cached__ = driver_partial(manager_cls().install())

    def configure_browser(self, browser="chrome", remote=False, headless=False, options=None, **kwargs):
        """Configure browser for session"""
        if browser not in _BROWSER_MAPPING:
            raise TypeError(f"Browser `{browser}`` is not supported. Select one of {_BROWSER_MAPPING.keys()}")

        if remote:
            self._browser = "remote"
        else:
            self._browser = browser or self._browser
        self._options = options or self._options or _OPTIONS_MAPPING[browser]()
        self._options.headless = headless
        self._other_options = kwargs or self._other_options or {}

    base_url = None

    def open(self, url: str):
        """Open given URL"""
        self.__init_browser()

        if self.base_url and not _FULL_URL_RE.fullmatch(url):
            if not url.startswith("/"):
                url = f"/{url}"
            url = f"{self.base_url}{url}"
        self.get_actual().get(url)

    @_check_browser
    def element(self, css_or_locator: CssSelectorOrBy) -> Element:
        """Find single element by locator (css selector by default)"""
        return super().element(css_or_locator)

    @_check_browser
    def elements(self, css_or_locator: CssSelectorOrBy) -> ElementCollection:
        """Find single element by locator (css selector by default)"""
        return super().elements(css_or_locator)

    @_check_browser
    def add_cookie(self, cookie_dict: dict):
        """Add cookies to cookie storage"""
        self.get_actual().add_cookie(cookie_dict)

    @_check_browser
    def close_window(self):
        """Close current browser window"""
        self.get_actual().close()

    @_check_browser
    def close_all_windows(self):
        """Close all browser windows"""
        self.get_actual().quit()

    @property
    def url(self) -> URL:
        """Get current page URL"""
        return URL(self.get_actual().current_url, self.base_url)

    def get_screenshot_as_png(self):
        """Make new page screenshot"""
        return self.get_actual().get_screenshot_as_png()


def _url_with_base(base_url: str, uri: str) -> str:
    if base_url is not None:
        if _FULL_URL_RE.fullmatch(uri):
            return uri
        if uri.startswith("/"):
            uri = uri[1:]
        return f"{base_url}/{uri}"
    return uri


class URL(NamedTuple):
    """Two-part URL"""
    url: str
    base_url: str = None

    def __eq__(self, other: str):
        this = _url_with_base(self.base_url, self.url)
        other = _url_with_base(self.base_url, other)
        return this == other
