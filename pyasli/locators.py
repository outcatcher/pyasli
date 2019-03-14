from abc import ABC, abstractmethod
from typing import Any, List, Tuple

from selenium.webdriver.remote.webelement import WebElement

from pyasli.searchable import Searchable


class LocatorStrategy(ABC):
    """Base class for locator containers"""

    def __init__(self, locator: Tuple[str, str], context: Searchable):
        self.context = context
        self.by = locator

    @abstractmethod
    def get(self) -> Any: ...


class MultipleElementLocator(LocatorStrategy):
    """Locator strategy for multiple elements"""

    def get(self) -> List[WebElement]:
        return self.context.get_actual().find_elements(*self.by)


class SingleElementLocator(LocatorStrategy):
    """Locator for returning single element"""

    def get(self) -> WebElement:
        """Get single web element"""
        return self.context.get_actual().find_element(*self.by)


class SlicedElementLocator(MultipleElementLocator):
    """Locator for returning slice from element collection"""

    def __init__(self, locator, context, slize: slice):
        super().__init__(locator, context)
        self.slize = slize

    def get(self) -> List[WebElement]:
        """Get slice from element collection"""
        elements = self.context.get_actual().find_elements(*self.by)
        return elements[self.slize]


class IndexElementLocator(SingleElementLocator):
    """Locator for returning element by index from collection"""

    def __init__(self, locator, context, index: int):
        super().__init__(locator, context)
        self.index = index

    def get(self) -> WebElement:
        """Get single element by index from collection"""
        elements = self.context.get_actual().find_elements(*self.by)
        return elements[self.index]
