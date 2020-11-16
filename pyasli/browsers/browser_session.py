"""Browser management"""

from __future__ import annotations

import atexit
import logging
import os
import re
from contextlib import AbstractContextManager
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Dict, NamedTuple, Optional, Type, Union

from selenium.webdriver import (
    Chrome, ChromeOptions, DesiredCapabilities, Firefox, FirefoxOptions, Ie, IeOptions, Remote
)
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager

from pyasli.bys import CssSelectorOrBy
from pyasli.elements.elements import Element, ElementCollection, FindElementsMixin
from pyasli.elements.searchable import LocatorStrategy, Searchable
from pyasli.exceptions import NoBrowserException, Screenshotable

LOG_FMT = '%(asctime)s - %(name)s - [%(levelname)s] %(message)s'

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

_FULL_URL_RE = re.compile(r"http(s)?://.+")


# noinspection PyTypeChecker
class BrowserLocatorStrategy(LocatorStrategy):
    """Root level locator strategy"""
    context: BrowserSession  # pylint: disable=used-before-assignment

    def get(self) -> Any:
        """Return actual browser"""
        raise NotImplementedError  # should not be used

    def __repr__(self) -> str:
        return self.context.browser_name.capitalize()

    def __init__(self, browser_session: BrowserSession):
        super().__init__(None, browser_session)


class BrowserSession(Searchable, FindElementsMixin, AbstractContextManager, Screenshotable):
    """Lazy webdriver wrapper"""

    _actual: Optional[Remote] = None
    __is_browser__ = True
    browser_name: str = None
    options = None
    desired_capabilities = None
    _other_options: dict = None
    logger: logging.Logger = None

    base_url: str = None

    @property
    def browser(self) -> BrowserSession:
        """Browser of browser is self XD"""
        return self  # pragma: no cover

    def _check_running(self):
        if self._actual is None:
            raise NoBrowserException("You should open some page before doing anything")

    def __init__(self, browser="chrome", base_url=None, log_path="./log"):
        """Init new lazy browser session.
        Setup browser to be used to given local headless browser
        """
        super().__init__(BrowserLocatorStrategy(self))
        self.setup_browser(browser)
        self.base_url = base_url
        # setup logging
        self._log_path = log_path
        self.logger = self._setup_logger()

        atexit.register(self.close_all_windows)

    def _setup_logger(self):
        logger = logging.getLogger(f'{__name__}.{self.browser_name}')
        logger.setLevel(logging.DEBUG)
        logger.propagate = True
        if not logger.hasHandlers():
            os.makedirs(self._log_path, exist_ok=True)
            file_handler = TimedRotatingFileHandler(
                f'{self._log_path}/{self.browser_name}.log',
                backupCount=2,
                utc=True,
                when='D'
            )
            file_handler.setLevel(logging.DEBUG)
            fmt = logging.Formatter(LOG_FMT)
            file_handler.setFormatter(fmt)
            logger.addHandler(file_handler)
        return logger

    @property
    def log_path(self):
        return self._log_path

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
        self.logger.debug('Starting %s ', self.browser_name)
        browser_cls = _BROWSER_MAPPING[self.browser_name]
        if browser_cls is Remote:
            self._actual = Remote(desired_capabilities=self.desired_capabilities, options=self.options,
                                  **self._other_options)
            return
        driver_path = _MANAGER_MAPPING[self.browser_name]().install()
        self._actual = browser_cls(executable_path=driver_path, options=self.options,
                                   desired_capabilities=self.desired_capabilities, **self._other_options)

    def set_driver(self, webdriver: Remote):
        """Override lazy driver initialization with already initialized webdriver"""
        self.logger.debug('Set driver to %s ', webdriver)
        if self._actual is not None:
            self.logger.debug('Driver already running, quit first')
            self._actual.quit()
        self._actual = webdriver

    def open(self, url: str):
        """Open given URL"""
        self.__init_browser()

        if self.base_url and not _FULL_URL_RE.fullmatch(url):
            if not url.startswith("/"):
                url = f"/{url}"
            url = f"{self.base_url}{url}"
        self.logger.debug('Open page at "%s"', url)
        self._actual.get(url)

    def element(self, by: CssSelectorOrBy) -> Element:
        """Find single element by locator (css selector by default)"""
        # pylint: disable=useless-super-delegation
        return super().element(by)

    def elements(self, by: CssSelectorOrBy) -> ElementCollection:
        """Find single element by locator (css selector by default)"""
        # pylint: disable=useless-super-delegation
        return super().elements(by)

    def add_cookie(self, cookie_dict: dict):
        """Add cookies to cookie storage"""
        self._check_running()
        self._actual.add_cookie(cookie_dict)

    def close_window(self):
        """Close current browser window"""
        self.logger.debug('Closing current browser window')
        self._check_running()
        self._actual.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_all_windows()

    def close_all_windows(self):
        """Close all browser windows"""
        self.logger.debug('Closing current all browser windows and quitting')
        actual = self._actual
        if actual is not None:
            actual.quit()
            self._actual = None

    @property
    def url(self) -> URL:
        """Get current page URL"""
        return URL(self._actual.current_url, self.base_url)

    def get_screenshot_as_png(self) -> bytes:
        """Capture whole browser page screenshot"""
        return self._actual.get_screenshot_as_png()

    capture_screenshot = get_screenshot_as_png

    def get_actual(self) -> WebDriver:
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

    def __str__(self):
        return _url_with_base(self.base_url, self.url)

    def __eq__(self, other):
        return str(self) == _url_with_base(self.base_url, str(other))

    def __ne__(self, other):
        return str(self) != _url_with_base(self.base_url, str(other))
