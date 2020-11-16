"""Pyasli entry point"""
import logging

from .browsers.browser_session import BrowserSession
from .browsers.shared_browser import browser
from .wait import wait_for

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
