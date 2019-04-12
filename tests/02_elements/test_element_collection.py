"""Element collection wrapper tests"""
import pytest
from selenium.common.exceptions import NoSuchElementException

from pyasli.browsers import BrowserSession
from pyasli.elements.elements import Element, ElementCollection


def test_collection_search(browser):
    browser.open("/dynamic_loading")
    examples = browser.elements("div#content a[href]")
    assert len(examples) == 2


def test_collection_get_single(browser):
    browser.open("/dynamic_loading")
    elem_loc = "div#content a[href]"
    examples = browser.elements(elem_loc)
    single = examples[0]
    assert isinstance(single, Element)
    assert single.text == "Example 1: Element on page that is hidden"


def test_collection_get_slice(browser):
    browser.open("/")
    refs = browser.elements("#content ul > li")
    ref_2_3 = refs[1:3]
    assert len(ref_2_3) == 2
    assert isinstance(ref_2_3, ElementCollection)
    assert isinstance(ref_2_3[0], Element)
    assert ref_2_3[0].text == "Add/Remove Elements"


def test_collection_children(browser):
    browser.open("/large")
    parents = browser.elements("div.example > div")
    single_child = parents.element("div#no-siblings")
    assert single_child.text == "No siblings"


def test_browser_from_nested_elements(browser):
    browser.open("/large")
    parent = browser.element("div.exapmple")
    child = parent.elements("div#siblings > div")
    assert isinstance(child.browser, BrowserSession)


def test_collections_filter(browser):
    browser.open("/")
    links = browser.elements("a[href]")
    total_length = len(links)
    not_checkboxes = links.filter(lambda l: l.text != "Checkboxes")
    assert total_length == len(not_checkboxes) + 1


def test_collections_find(browser):
    browser.open("/")
    links = browser.elements("a[href]")
    checkbox = links.find(lambda l: l.text == "Checkboxes")
    assert isinstance(checkbox, Element)
    assert checkbox.text == "Checkboxes"


def test_collections_filter_children(browser):
    browser.open("/login")
    form_elements = browser.elements("form#login > *")
    inputs = form_elements.filter(lambda e: e.tag_name == "div")
    username_input = inputs.element("input[name=username]")
    assert isinstance(username_input, Element)
    assert username_input.get_attribute("id") == "username"


def test_collections_find_children(browser):
    browser.open("/login")
    form_elements = browser.elements("form#login > *")
    inputs = form_elements.find(lambda e: e.tag_name == "div")
    username_input = inputs.element("input[name=username]")
    assert isinstance(username_input, Element)
    assert username_input.get_attribute("id") == "username"


def test_assure_all(browser):
    browser.open("/login")
    form_elements = browser.elements("form#login > div")
    form_elements.assure_all(lambda e: e.get_attribute("class") == "row")


def test_assure_all_negative(browser):
    browser.open("/login")
    form_elements = browser.elements("form#login > *")
    with pytest.raises(TimeoutError):
        form_elements.assure_all(lambda e: e.get_attribute("class") == "row", timeout=0.1)


def test_negative_filter(browser):
    browser.open("/login")
    form_elements = browser.elements("form#login > *")
    assert len(form_elements.filter(lambda e: False)) == 0


def test_negative_find(browser):
    browser.open("/login")
    form_elements = browser.elements("form#login > *")
    nothing = form_elements.find(lambda e: False)  # dead filter
    with pytest.raises(NoSuchElementException):
        nothing.get_actual()
