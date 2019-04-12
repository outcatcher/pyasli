"""repr() tests for Element Collections and Elements"""
import pytest


class TestCollectionsRepr:

    @pytest.fixture(scope="class")
    def __examples(self, browser):
        browser.open("/dynamic_loading")
        elem_loc = "div#content a[href]"
        return browser.elements(elem_loc), elem_loc, browser.browser_name.capitalize()

    @pytest.mark.parametrize(["slc", "desc"],
                             [
                                 (slice(1, 2), "[1:2]"),
                                 (slice(1, 4, 2), "[1:4:2]"),
                                 (slice(2), "[:2]"),
                                 (slice(2, None), "[2:]"),
                                 (slice(None, None), "[:]"),
                             ])
    def test_slice_repr(self, __examples, slc, desc):
        examples, elem_loc, name = __examples
        assert repr(examples[slc]) == f"Element Collection by: {name} -> [('css selector', '{elem_loc}')]{desc}"

    def test_index_repr(self, __examples):
        examples, elem_loc, name = __examples
        assert repr(examples[1]) == f"Element by: {name} -> [('css selector', '{elem_loc}')][1]"

    def test_collection_repr(self, __examples):
        examples, elem_loc, name = __examples
        assert repr(examples) == f"Element Collection by: {name} -> [('css selector', '{elem_loc}')]"

    def test_filter_repr(self, __examples):
        examples, _, _ = __examples

        def _my_cond(el):
            return bool(el)

        filtered = examples.filter(_my_cond)
        assert repr(filtered) == f"{repr(examples)}.filter(_my_cond)"

    def test_find_repr(self, __examples):
        examples, elem_loc, name = __examples

        def _my_cond(el):
            return bool(el)

        found = examples.find(_my_cond)
        assert repr(found) == f"Element by: {name} -> [('css selector', '{elem_loc}')].find(_my_cond)"

    def test_index_in_slice(self, __examples):
        examples, elem_loc, name = __examples
        assert repr(examples[:3][1]) == f"Element by: {name} -> [('css selector', '{elem_loc}')][:3][1]"

    def test_slice_in_filter(self, __examples):
        examples, elem_loc, name = __examples

        def _my_cond(el):
            return bool(el)

        found = examples.filter(_my_cond)
        assert repr(found[1:3]) == f"Element Collection by: {name} -> [('css selector', '{elem_loc}')]" \
            f".filter(_my_cond)[1:3]"


def test_element_repr(browser):
    browser.open("/dynamic_loading/1")
    loading = browser.element("div#loading")
    assert repr(loading) == f"Element by: {browser.browser_name.capitalize()} -> ('css selector', 'div#loading')"
