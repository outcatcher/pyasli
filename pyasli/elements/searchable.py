"""Base classes for searchable element implementations"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Union

from selenium.webdriver import Remote
from selenium.webdriver.remote.webelement import WebElement

Wrapped = Union[WebElement, List[WebElement], Remote]
BROWSER = "Browser"


class Searchable(ABC):
    """Base class for objects that presents lazy-loading searchable elements"""

    __cached__: Wrapped = None
    __is_browser__ = False
    _locator: LocatorStrategy

    def __init__(self, locator: LocatorStrategy):
        self._locator = locator

    def get_actual(self):
        """Get actual instance of wrapped class"""
        if self.__cached__ is None:
            self.__cached__ = self._search()
        return self.__cached__

    def _search(self) -> Wrapped:
        return self._locator.get()

    @property
    def browser(self):
        """Return used browser instance"""
        # pylint: disable=protected-access
        parent_locator = self._locator
        while not parent_locator.context.__is_browser__:
            parent_locator = parent_locator.context._locator
        return parent_locator.context


class LocatorStrategy(ABC):
    """Base class for locator containers"""

    context: Searchable

    def __init__(self, by: Tuple[str, str], context: Searchable):
        self.context = context
        self.by = by

    @abstractmethod
    def get(self) -> Any:
        """"Run locator and return object"""

    @abstractmethod
    def __repr__(self) -> str: ...  # pylint: disable=multiple-statements
