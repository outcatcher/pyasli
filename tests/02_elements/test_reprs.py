"""repr() tests for Element Collections and Elements"""
import pytest


class TestCollectionsRepr:

    @pytest.fixture(scope="class")
    def __examples(self, browser):
        browser.open("/dynamic_loading")
        elem_loc = "div#content a[href]"
        return browser.elements(elem_loc), elem_loc

    @pytest.mark.parametrize(["slc", "desc"],
                             [
                                 (slice(1, 2), "[1:2]"),
                                 (slice(1, 4, 2), "[1:4:2]"),
                                 (slice(2), "[:2]"),
                                 (slice(2, None), "[2:]"),
                                 (slice(None, None), "[:]"),
                             ])
    def test_slice_repr(self, __examples, slc, desc):
        examples, elem_loc = __examples
        assert repr(examples[slc]) == f"Element Collection by: 'Browser' -> [('css selector', '{elem_loc}')]{desc}"

    def test_index_repr(self, __examples):
        examples, elem_loc = __examples
        assert repr(examples[1]) == f"Element by: 'Browser' -> [('css selector', '{elem_loc}')][1]"

    def test_collection_repr(self, __examples):
        examples, elem_loc = __examples
        assert repr(examples) == f"Element Collection by: 'Browser' -> [('css selector', '{elem_loc}')]"


def test_element_repr(browser):
    browser.open("/dynamic_loading/1")
    loading = browser.element("div#loading")
    assert repr(loading) == f"Element by: 'Browser' -> ('css selector', 'div#loading')"
