"""WebElement wrappers"""
from __future__ import annotations

from itertools import chain
from typing import Sequence, overload

from selenium.common.exceptions import WebDriverException

from pyasli.bys import ByLocator, CssSelectorOrBy, by_css
from pyasli.conditions import wait_for
from pyasli.locators import *
from pyasli.searchable import Searchable, Wrapped


def _element_is_dead(element: WebElement):
    try:
        _ = element.location
        return False
    except WebDriverException:
        return True


def _css_to_by(by: CssSelectorOrBy) -> ByLocator:
    if isinstance(by, tuple):
        return by
    return by_css(by)


class SearchableWithElements(Searchable, ABC):
    """Implemented `element` and `elements` methods"""

    def __init__(self, locator: LocatorStrategy):
        self.locator = locator

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


class Element(SearchableWithElements):
    """Single lazy element"""

    def __init__(self, locator: LocatorStrategy):
        super().__init__(locator)
        self.assure = Assure(self)

    def _search(self) -> WebElement:
        return super()._search()

    def click(self):
        """Click web element"""
        self.get_actual().click()


def _flatten_list(list_of_lists):
    return list(chain.from_iterable(list_of_lists))


class ElementCollection(SearchableWithElements, Sequence):
    """Collection of lazy elements"""

    def __init__(self, locator: MultipleElementLocator):  # all hail type hints
        super().__init__(self, locator)

    @overload
    def __getitem__(self, index: int) -> Element:
        return Element(IndexElementLocator(self.locator.by, self, index))

    def __getitem__(self, slize: slice) -> ElementCollection:
        return ElementCollection(SlicedElementLocator(self.locator.by, self, slize))

    def __len__(self) -> int:
        return len(self.get_actual())


class Assure:
    """Class for conditions"""

    __slots__ = ["element"]

    def __init__(self, element: Searchable):
        self.element = element

    def visible(self):
        """Assure element is visible"""
        wait_for(self.element.get_actual().is_displayed)

    def hidden(self):
        """Assure element is hidden"""
        wait_for(lambda: not self.element.get_actual().is_displayed())
