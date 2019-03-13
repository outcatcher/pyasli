from __future__ import annotations

import atexit
from typing import Dict, Type

import wrapt
from selenium.webdriver import Chrome, ChromeOptions, Firefox, FirefoxOptions, Ie, IeOptions, Remote

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


class BrowserSession:
    """Class containing single webdriver instance and all browser operations"""

    _web_driver: Remote = None
    _browser: str = None
    _options = None
    _other_options: dict = None

    def __init__(self, browser="chrome", remote=False, options=None, **kwargs):
        """Init new browser session.
        Arguments for creating webdriver instance other than ``options`` should be passed to kwargs
        """
        self.configure_browser(browser, remote, options, **kwargs)
        atexit.register(self.close_all_windows)

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

    def close_all_windows(self):
        """Close all browser windows"""
        self._web_driver.quit()


shared = BrowserSession()


def set_browser(browser: str):
    """Set shared session browser"""
    shared.configure_browser(browser=browser)


def set_options(options):
    """Set shared session options"""
    shared.configure_browser(options=options)
