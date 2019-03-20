"""WebElement wrappers"""
from __future__ import annotations

from abc import ABC
from typing import List, Sequence, Type, Union

from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver import Remote
from selenium.webdriver.remote.webelement import WebElement

from pyasli.bys import ByLocator, CssSelectorOrBy, by_css
from pyasli.locators import (
    IndexElementLocator, LocatorStrategy, MultipleElementLocator, SingleElementLocator, SlicedElementLocator
)
from pyasli.wait import wait_for


def _css_to_by(by: CssSelectorOrBy) -> ByLocator:
    if isinstance(by, tuple):
        return by
    return by_css(by)


Wrapped = Union[WebElement, List[WebElement], Remote]

BROWSER = "Browser"


class Searchable(ABC):
    """Implemented `element` and `elements` methods"""

    __cached__: Wrapped = None

    def __init__(self, locator: LocatorStrategy):
        self.locator = locator

    def get_actual(self):
        """Get actual instance of wrapped class"""
        if self.__cached__ is None:
            self.__cached__ = self._search()
        return self.__cached__

    def element(self, by: CssSelectorOrBy) -> Element:
        """Search for single child element"""
        by = _css_to_by(by)
        return Element(SingleElementLocator(by, self))

    def elements(self, by: CssSelectorOrBy) -> ElementCollection:
        """Search for multiple child elements"""
        by = _css_to_by(by)
        return ElementCollection(MultipleElementLocator(by, self))

    def _search(self) -> Wrapped:
        return self.locator.get()

    @property
    def browser(self):
        """Return used browser instance"""
        parent_locator = self.locator
        while parent_locator.context.locator != BROWSER:
            parent_locator = parent_locator.context.locator
        return parent_locator.context


class Element(Searchable):
    """Single lazy element"""

    def __init__(self, locator: LocatorStrategy):
        super().__init__(locator)
        self.parent = locator.context
        self.assure = Assure(self)
        self.should_be = Assure(self, AssertionError)
        self.should = self.should_be

    def _search(self) -> WebElement:
        return super()._search()

    def _element_is_dead(self):
        try:
            _ = self.__cached__.location
            return False
        except WebDriverException:
            return True

    def get_actual(self):
        """Get element, check if it's cached or already dead"""
        if (self.__cached__ is None) or self._element_is_dead():
            self.__cached__ = self._search()
        return self.__cached__

    def click(self):
        """Click web element"""
        self.assure.visible()
        self.get_actual().click()

    @property
    def text(self) -> str:
        """Get element text"""
        self.assure.visible()
        return self.get_actual().text

    @text.setter
    def text(self, value: str):
        """Set element text (if possible)"""
        self.assure.visible()
        self.get_actual().clear()
        self.get_actual().send_keys(value)

    def is_visible(self):
        """Check if element is visible"""
        if not self.exists():
            return False
        return self.get_actual().is_displayed()

    def is_hidden(self):
        """Check if element is hidden"""
        return not self.is_visible()

    def exists(self):
        """Check if element exists in dom"""
        try:
            self.get_actual()
            return True
        except NoSuchElementException:
            return False

    def __repr__(self):
        return f"Element by: {repr(self.locator)}"


class ElementCollection(Searchable, Sequence):
    """Collection of lazy elements"""

    locator: MultipleElementLocator

    def __init__(self, locator: MultipleElementLocator):  # all hail type hints
        super().__init__(locator)

    def __getitem__(self, index: Union[int, slice]) -> Union[Element, ElementCollection]:
        if isinstance(index, slice):
            return ElementCollection(SlicedElementLocator(self.locator, index))
        return Element(IndexElementLocator(self.locator, index))

    def __len__(self) -> int:
        return len(self.get_actual())

    def __repr__(self):
        return f"Element Collection by: {repr(self.locator)}"


class Assure:
    """Class for conditions"""

    __slots__ = ["element", "exception"]
    DEFAULT_TIMEOUT = 5

    def __init__(self, element: Searchable, exception: Union[Type[Exception], Exception] = None):
        self.element = element
        self.exception = exception

    def visible(self, timeout=DEFAULT_TIMEOUT):
        """Assure element is visible"""
        wait_for(self.element, lambda x: x.is_visible(), timeout, self.exception)

    def hidden(self, timeout=DEFAULT_TIMEOUT):
        """Assure element is hidden"""
        wait_for(self.element, lambda x: x.is_hidden(), timeout, self.exception)

    def exist(self, timeout=DEFAULT_TIMEOUT):
        """Assure element exists in DOM"""
        wait_for(self.element, lambda x: x.exists(), timeout, self.exception)
