"""Lazy locator wrappers"""
from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Union

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement


def _search_in_context(context: "Searchable", method: str, by: tuple) -> List[WebElement]:
    actual = context.get_actual()
    if not isinstance(actual, list):
        actual: List[WebElement] = [actual]
    result = []
    for elem in actual:
        try:
            found = getattr(elem, method)(*by)
        except NoSuchElementException:
            continue
        if isinstance(found, list):
            result.extend(found)  # append or extend depending on result of search
        else:
            result.append(found)
    if not result:
        raise NoSuchElementException
    return result


class LocatorStrategy(ABC):
    """Base class for locator containers"""

    def __init__(self, by: Tuple[str, str], context: "Searchable"):
        self.context = context
        self.by = by

    @abstractmethod
    def get(self) -> Any:
        """"Run locator and return object"""

    @abstractmethod
    def __repr__(self) -> str:
        ...


class MultipleElementLocator(LocatorStrategy):
    """Locator strategy for multiple elements"""

    def get(self) -> List[WebElement]:
        """Get list of matching web elements"""
        return _search_in_context(self.context, "find_elements", self.by)

    def __repr__(self):
        # recursive repr
        return f"{repr(self.context.locator)} -> [{self.by}]"


class SingleElementLocator(LocatorStrategy):
    """Locator for returning single element"""

    def get(self) -> WebElement:
        """Get single matching web element"""
        result = _search_in_context(self.context, "find_element", self.by)
        return result[0]

    def __repr__(self):
        # recursive repr
        return f"{repr(self.context.locator)} -> {self.by}"


class SubElementLocator(LocatorStrategy):
    """Locator for elements extracted from element list"""

    def __init__(self, whole: MultipleElementLocator, sub: Union[slice, int]):
        super().__init__(whole.by, whole.context)
        self._whole = whole
        self._sub = sub

    def get(self) -> List[WebElement]:
        """Get slice from element collection (not going deeper)"""
        elements = self._whole.get()
        return elements[self._sub]

    def __repr__(self):
        # recursive repr
        return f"{repr(self._whole)}[{self._sub}]"


class SlicedElementLocator(SubElementLocator, MultipleElementLocator):
    """Locator for returning slice from element collection"""

    def __init__(self, whole: MultipleElementLocator, slize: slice):
        super().__init__(whole, slize)

    def __repr__(self):
        # recursive repr
        start = "" if self._sub.start is None else self._sub.start
        stop = "" if self._sub.stop is None else self._sub.stop
        sss = f"{start}:{stop}"
        if self._sub.step:
            sss = f"{sss}:{self._sub.step}"
        return f"{repr(self._whole)}[{sss}]"


class IndexElementLocator(SubElementLocator, SingleElementLocator):
    """Locator for returning element by index from collection"""

    def __init__(self, whole: MultipleElementLocator, index: int):
        super().__init__(whole, index)
