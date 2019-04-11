"""Browser management"""

from __future__ import annotations

import atexit
import re
from typing import Dict, NamedTuple, Type, Union

from selenium.webdriver import (
    Chrome, ChromeOptions, DesiredCapabilities, Firefox, FirefoxOptions, Ie, IeOptions, Remote
)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager

from pyasli.bys import CssSelectorOrBy
from pyasli.elements.elements import Element, ElementCollection, FindElementsMixin
from pyasli.elements.searchable import BROWSER, Searchable

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


_FULL_URL_RE = re.compile(r"http(s)?://.+")


class BrowserSession(Searchable, FindElementsMixin):
    """Class containing single webdriver instance and all browser operations"""

    _actual: Remote = None
    __is_browser__ = True
    browser_name: str = None
    options = None
    desired_capabilities = None
    _other_options: dict = None

    def _check_running(self):
        if self._actual is None:
            raise NoBrowserException("You should open some page before doing anything")

    def __init__(self, browser="chrome"):
        """Init new browser session.
        Setup browser to be used to given local headless browser
        """
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

    def __init_browser(self):
        """Start new browser instance"""
        if self._actual is not None:
            return
        browser_cls = _BROWSER_MAPPING[self.browser_name]
        if browser_cls is Remote:
            self._actual = Remote(desired_capabilities=self.desired_capabilities, options=self.options,
                                  **self._other_options)
            return
        driver_path = _MANAGER_MAPPING[self.browser_name]().install()
        if browser_cls is Firefox:
            self._actual = Firefox(executable_path=driver_path, options=self.options,
                                   desired_capabilities=self.desired_capabilities, **self._other_options)
        else:
            self._actual = browser_cls(driver_path, options=self.options, **self._other_options)

    def set_driver(self, webdriver: Remote):
        """Override lazy driver initialization with already initialized webdriver"""
        if self._actual is not None:
            self._actual.quit()
        self._actual = webdriver

    base_url = None

    def open(self, url: str):
        """Open given URL"""
        self.__init_browser()

        if self.base_url and not _FULL_URL_RE.fullmatch(url):
            if not url.startswith("/"):
                url = f"/{url}"
            url = f"{self.base_url}{url}"
        self._actual.get(url)

    def element(self, by: CssSelectorOrBy) -> Element:
        """Find single element by locator (css selector by default)"""
        self._check_running()
        return super().element(by)

    def elements(self, by: CssSelectorOrBy) -> ElementCollection:
        """Find single element by locator (css selector by default)"""
        self._check_running()
        return super().elements(by)

    def add_cookie(self, cookie_dict: dict):
        """Add cookies to cookie storage"""
        self._check_running()
        self._actual.add_cookie(cookie_dict)

    def close_window(self):
        """Close current browser window"""
        self._check_running()
        self._actual.close()

    def close_all_windows(self):
        """Close all browser windows"""
        actual = self._actual
        if actual is not None:
            actual.quit()

    @property
    def url(self) -> URL:
        """Get current page URL"""
        return URL(self._actual.current_url, self.base_url)

    def get_screenshot_as_png(self):
        """Make new page screenshot"""
        return self._actual.get_screenshot_as_png()

    def get_actual(self):
        """Get browser instance"""
        return self._actual


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
