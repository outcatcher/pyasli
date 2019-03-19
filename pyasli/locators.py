"""Lazy locator wrappers"""

from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Union

from selenium.webdriver.remote.webelement import WebElement


class LocatorStrategy(ABC):
    """Base class for locator containers"""

    def __init__(self, locator: Tuple[str, str], context: "Searchable"):
        self.context = context
        self.by = locator

    @abstractmethod
    def get(self) -> Any:
        """"Run locator and return object"""

    @abstractmethod
    def __repr__(self) -> str: ...


class MultipleElementLocator(LocatorStrategy):
    """Locator strategy for multiple elements"""

    def get(self) -> List[WebElement]:
        """Get list of matching web elements"""
        return self.context.get_actual().find_elements(*self.by)

    def __repr__(self):
        # recursive repr
        return f"{repr(self.context.locator)} -> [{self.by}]"


class SingleElementLocator(LocatorStrategy):
    """Locator for returning single element"""

    def get(self) -> WebElement:
        """Get single matching web element"""
        return self.context.get_actual().find_element(*self.by)

    def __repr__(self):
        # recursive repr
        return f"{repr(self.context.locator)} -> {self.by}"


class SubElementLocator(LocatorStrategy):
    """Locator for elements extracted from element list"""

    def __init__(self, locator, context: "ElementCollection", sub: Union[slice, int]):
        super().__init__(locator, context)
        self.sub = sub

    def get(self) -> List[WebElement]:
        """Get slice from element collection (not going deeper)"""
        elements = self.context.get_actual()
        return elements[self.sub]

    def __repr__(self):
        # recursive repr
        return f"{repr(self.context.locator)}[{self.sub}]"


class SlicedElementLocator(SubElementLocator, MultipleElementLocator):
    """Locator for returning slice from element collection"""

    def __init__(self, locator, context, slize: slice):
        super().__init__(locator, context, slize)

    def __repr__(self):
        # recursive repr
        start = "" if self.sub.start is None else self.sub.start
        stop = "" if self.sub.stop is None else self.sub.stop
        sss = f"{start}:{stop}"
        if self.sub.step:
            sss = f"{sss}:{self.sub.step}"
        return f"{repr(self.context.locator)}[{sss}]"


class IndexElementLocator(SubElementLocator, SingleElementLocator):
    """Locator for returning element by index from collection"""

    def __init__(self, locator, context, index: int):
        super().__init__(locator, context, index)
