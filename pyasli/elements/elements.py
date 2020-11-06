"""WebElement wrappers"""
from __future__ import annotations

import time
from typing import Callable, Sequence, Union

import wrapt
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from pyasli.bys import ByLocator, CssSelectorOrBy, by_css, by_xpath
from pyasli.elements.locators import (
    FilteredCollectionLocator, FindElementLocator, IndexElementLocator, MultipleElementLocator,
    SingleElementLocator, SlicedElementLocator
)
from pyasli.elements.searchable import Searchable
from pyasli.exceptions import NoBrowserException, Screenshotable, screenshot_on_fail
from pyasli.wait import wait_for


# pylint: disable=fixme

@wrapt.decorator
def _stale_retry(wrapped, instance: Element = None, args=None, kwargs=None):
    try:
        return wrapped(*args, **kwargs)
    except StaleElementReferenceException:
        instance.__cached__ = None  # invalidate cache
        return wrapped(*args, **kwargs)


@wrapt.decorator
def _should_exist(wrapped, instance: Element = None, args=(), kwargs=None):
    """Check for element existence before run method

    This decorator uses `assure`, so screenshot will be taken automatically on fail
    """
    if instance is None:
        instance = args[0]

    def _exists(_el):
        return _el.exists

    instance.assure(_exists)
    return wrapped(*args, **kwargs)


def _css_to_by(by: CssSelectorOrBy) -> ByLocator:
    if isinstance(by, tuple):
        return by
    return by_css(by)


class FindElementsMixin:
    """Adding `element` and `elements` methods to class"""

    def element(self, by: CssSelectorOrBy) -> Element:
        """Search for single child element"""
        by = _css_to_by(by)
        return Element(SingleElementLocator(by, self))

    def elements(self, by: CssSelectorOrBy) -> ElementCollection:
        """Search for multiple child elements"""
        by = _css_to_by(by)
        return ElementCollection(MultipleElementLocator(by, self))


class Element(Searchable, FindElementsMixin, Screenshotable):
    """Single lazy element"""

    @screenshot_on_fail
    def __wait_for_condition(self, condition, timeout, exception_cls):
        exception = exception_cls(f"Condition {condition.__name__} is not reached in {timeout} seconds for {self}")
        wait_for(self, condition, timeout, exception)

    def assure(self, condition, timeout=5):
        """Make sure that element matches condition or raises :class:`TimeoutError`"""
        self.__wait_for_condition(condition, timeout, TimeoutError)

    def should(self, condition, timeout=5):
        """Make sure that element matches condition or raises :class:`AssertionError`"""
        self.__wait_for_condition(condition, timeout, AssertionError)

    should_be = should

    def get_actual(self) -> WebElement:
        """Get element, check if it's cached or already dead"""
        if self.browser.get_actual() is None:
            raise NoBrowserException
        return super().get_actual()

    def _actions(self):
        return ActionChains(self.browser.get_actual())

    @_stale_retry
    @_should_exist
    def move_to(self):
        """Scroll to the element"""
        self._actions().move_to_element(self.get_actual()).perform()

    @_stale_retry
    @_should_exist
    def click(self):
        """Click web element"""
        self._actions().click(self.get_actual()).perform()

    @_stale_retry
    @_should_exist
    def double_click(self):
        """Make double click on the element"""
        self._actions().double_click(self.get_actual()).perform()

    @_stale_retry
    @_should_exist
    def hover(self):
        """Hover over element"""
        self._actions().move_to_element(self.get_actual()).perform()

    @_stale_retry
    @_should_exist
    def right_click(self):
        """Open context menu"""
        self._actions().context_click(self.get_actual()).perform()

    @property
    @_stale_retry
    @_should_exist
    def text(self) -> str:
        """Get element text"""
        return self.get_actual().text

    @text.setter
    @_stale_retry
    @_should_exist
    def text(self, value: str):
        """Set element text (if possible)"""
        self.clear()
        self.get_actual().send_keys(value)

    @property
    def value(self):
        """Get element @value attribute"""
        return self.get_attribute("value")

    @property
    @screenshot_on_fail
    @_stale_retry
    def visible(self):
        """Check if element is visible"""
        if not self.exists:
            return False
        return self.get_actual().is_displayed()

    @property
    def hidden(self):
        """Check if element is hidden"""
        return not self.visible

    @property
    @screenshot_on_fail
    def exists(self):
        """Check if element exists in dom"""
        try:
            self._search()
            return True
        except NoSuchElementException:
            return False

    @property
    @_stale_retry
    @_should_exist
    def selected(self):
        """Return element selected state"""
        return self.get_actual().is_selected()

    @property
    @_stale_retry
    @_should_exist
    def tag_name(self):
        """Get element tag name"""
        return self.get_actual().tag_name

    @_stale_retry
    @_should_exist
    def get_attribute(self, name: str):
        """Get WebElement attribute value"""
        return self.get_actual().get_attribute(name)

    @_stale_retry
    @_should_exist
    def clear(self):
        """Clear input field"""
        self.get_actual().clear()

    # TODO: re-enable if become useful
    # @_should_exit
    # def get_property(self, name):
    #     """Gets the given property of the element"""
    #     self.get_actual().get_property(name)

    @property
    @_stale_retry
    @_should_exist
    def enabled(self):
        """Return element enabled state"""
        _enabled = self.get_actual().is_enabled()
        _disabled = (
                self.get_attribute("disabled") is not None
                or
                self.get_attribute("aria-disabled") is not None
        )
        return _enabled and not _disabled

    @property
    def disabled(self):
        """Return element disabled state"""
        return not self.enabled

    @property
    @_stale_retry
    @_should_exist
    def size(self):
        """Element size"""
        return self.get_actual().size

    # TODO: re-enable if become useful
    # @_should_exit
    # def value_of_css_property(self, name):
    #     """Returns value css property"""
    #     return self.get_actual().value_of_css_property(name)

    @property
    @_should_exist
    def parent(self):
        """Return parent element of given one"""
        return self.element(by_xpath("./.."))

    @_stale_retry
    @_should_exist
    def element(self, by: CssSelectorOrBy) -> Element:
        return super().element(by)

    @_stale_retry
    @_should_exist
    def elements(self, by: CssSelectorOrBy) -> ElementCollection:
        return super().elements(by)

    def ancestors(self, filter_condition: ElementCondition = None):
        """Return parent element chain from parent element to `html`"""
        ancestors = self.elements(by_xpath("./ancestor::*"))
        if filter_condition is None:
            return ancestors
        return ancestors.filter(filter_condition)

    def neighbours(self, filter_condition: ElementCondition = None):
        """Get all elements on current level filtered by condition if given"""
        elements = self.parent.elements(by_xpath("./*"))
        if filter_condition is None:
            return elements
        return elements.filter(filter_condition)

    def capture_screenshot(self) -> bytes:
        """Capture single element screenshot"""
        try:
            return self.get_actual().screenshot_as_png
        except WebDriverException:  # if get_actual has failed
            return self.browser.capture_screenshot()

    def __repr__(self):
        return f"Element by: {repr(self._locator)}"

    def __getattr__(self, item) -> str:
        """Return value of element attribute with given name as string"""
        return self.get_attribute(item)


ElementCondition = Callable[[Element], bool]


class ElementCollection(Searchable, FindElementsMixin, Sequence):  # pylint: disable=inherit-non-class
    """Collection of lazy elements"""

    _locator: MultipleElementLocator

    def __init__(self, locator: MultipleElementLocator):  # all hail type hints
        super().__init__(locator)

    def __getitem__(self, index: Union[int, slice]) -> Union[Element, ElementCollection]:
        if isinstance(index, slice):
            return ElementCollection(SlicedElementLocator(self._locator, index))
        length = len(self)
        if 0 <= index < length:
            return Element(IndexElementLocator(self._locator, index))
        raise IndexError(f"Collection index {index} is out of range (0..{length})")

    def __len__(self) -> int:
        return len(self.get_actual())

    def __repr__(self):
        return f"Element Collection by: {repr(self._locator)}"

    def filter(self, condition: Callable[[Element], bool]):
        """Filter list of collection elements filtered by condition applied to `Element`"""
        return ElementCollection(FilteredCollectionLocator(self, condition))

    def find(self, condition: Callable[[Element], bool]):
        """Find single collection element by condition"""
        return Element(FindElementLocator(self, condition))

    def assure_all(self, condition, timeout=5, exception=TimeoutError):
        """Assure condition matches for all elements"""
        end_time = time.time() + timeout
        full_length = len(self)
        matching = None
        while time.time() < end_time:
            matching = self.filter(condition)
            if len(matching) == full_length:
                return
        raise exception(f"{full_length - len(matching)} elements are not matching condition")
