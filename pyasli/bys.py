"""Locator techniques"""
from typing import Tuple, Union

from selenium.webdriver.common.by import By

ByLocator = Tuple[str, str]

CssSelectorOrBy = Union[str, ByLocator]


def by_id(element_id: str) -> ByLocator:
    """By ID"""
    return By.ID, element_id


def by_css(css_selector: str) -> ByLocator:
    """By css selector"""
    return By.CSS_SELECTOR, css_selector


def by_xpath(xpath: str) -> ByLocator:
    """By xpath"""
    return By.XPATH, xpath


def by_name(name: str) -> ByLocator:
    """By name"""
    return By.NAME, name


def by_class(cls: str) -> ByLocator:
    """By class name"""
    return By.CLASS_NAME, cls


def by_tag(tag: str) -> ByLocator:
    """By tag name"""
    return By.TAG_NAME, tag
