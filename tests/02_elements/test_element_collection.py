"""Element collection wrapper tests"""
from pyasli.browser import BrowserSession
from pyasli.elements import Element, ElementCollection


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
    assert ref_2_3[1].text == "Broken Images"


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
