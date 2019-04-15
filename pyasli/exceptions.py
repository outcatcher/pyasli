from selenium.common.exceptions import WebDriverException


class NoBrowserException(WebDriverException):
    """No operatable browser is open"""
