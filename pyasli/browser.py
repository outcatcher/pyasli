"""Browser management"""

from __future__ import annotations

import atexit
import re
from typing import Dict, NamedTuple, Type, Union

import wrapt
from selenium.webdriver import (
    Chrome, ChromeOptions, DesiredCapabilities, Firefox, FirefoxOptions, Ie, IeOptions, Remote
)
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
    browser_name: str = None
    options = None
    desired_capabilities = None
    _other_options: dict = None

    def __init__(self, browser="chrome"):
        """Init new browser session.
        Setup browser to be used to given local headless browser
        """
        # noinspection PyTypeChecker
        super().__init__(BROWSER)
        self.setup_browser(browser)
        atexit.register(self.close_all_windows)

    def setup_browser(self, browser: str, remote=False, headless=True,
                      options: Union[ChromeOptions, FirefoxOptions, IeOptions] = None,
                      desired_capabilities: DesiredCapabilities = None,
                      **other_options):
        """Configure browser to be used

        :param str browser: Name of browser to be used
        :param bool remote: Is used browser running on remote host.
            In this case you should set `command_executor` argument to desired host value
        :param bool headless: If `options` are not set, control `headless` option
        :param options: Browser options
        :param desired_capabilities: Browser desired capabilities
        :param other_options: Other options which will be passed to WebDriver constructor
        """
        if remote:
            self.browser_name = "remote"
            self.options = options or _OPTIONS_MAPPING[browser]()
        else:
            self.browser_name = browser
            self.options = options
        if options is None:
            self.options = _OPTIONS_MAPPING[browser]()
            self.options.headless = headless
        self.desired_capabilities = desired_capabilities
        self._other_options = other_options

    def _search(self) -> Wrapped:
        return self.__cached__

    def __init_browser(self):
        """Start new browser instance"""
        if self.__cached__ is not None:
            return
        browser_cls = _BROWSER_MAPPING[self.browser_name]
        if browser_cls is Remote:
            self.__cached__ = Remote(desired_capabilities=self.desired_capabilities, options=self.options,
                                     **self._other_options)
            return
        driver_path = _MANAGER_MAPPING[self.browser_name]().install()
        if browser_cls is Firefox:
            self.__cached__ = Firefox(executable_path=driver_path, options=self.options,
                                      desired_capabilities=self.desired_capabilities, **self._other_options)
        else:
            self.__cached__ = browser_cls(driver_path, options=self.options, **self._other_options)

    def set_driver(self, webdriver: Remote):
        """Override lazy driver initialization with already initialized webdriver"""
        if self.__cached__ is not None:
            self.__cached__.quit()
        self.__cached__ = webdriver

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
    def element(self, by: CssSelectorOrBy) -> Element:
        """Find single element by locator (css selector by default)"""
        return super().element(by)

    @_check_browser
    def elements(self, by: CssSelectorOrBy) -> ElementCollection:
        """Find single element by locator (css selector by default)"""
        return super().elements(by)

    @_check_browser
    def add_cookie(self, cookie_dict: dict):
        """Add cookies to cookie storage"""
        self.get_actual().add_cookie(cookie_dict)

    @_check_browser
    def close_window(self):
        """Close current browser window"""
        self.get_actual().close()

    def close_all_windows(self):
        """Close all browser windows"""
        actual = self.get_actual()
        if actual is not None:
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
