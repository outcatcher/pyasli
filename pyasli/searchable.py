from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Union

from selenium.webdriver import Remote
from selenium.webdriver.remote.webelement import WebElement

Wrapped = Union[WebElement, List[WebElement], Remote]


class Searchable(ABC):
    """Base class objects with ability to find element(s)"""

    __cached__: Wrapped = None

    @abstractmethod
    def _search(self) -> Wrapped:
        """Runs search for given element inside of parent"""

    @abstractmethod
    def element(self, by) -> Searchable:
        """Find child element"""

    @abstractmethod
    def elements(self, by) -> Searchable:
        """Find multiple child elements"""

    def get_actual(self):
        """Get actual instance of wrapped class"""
        if self.__cached__ is None:
            self.__cached__ = self._search()
        return self.__cached__
