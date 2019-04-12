"""Element wrapper tests"""

import pytest

from pyasli.browsers import BrowserSession
from pyasli.bys import by_css
from pyasli.conditions import exist, hidden, visible
from pyasli.elements.elements import Element


def test_caching(browser):
    browser.open("/disappearing_elements")
    element1 = browser.element("div.example p")
    assert element1.get_actual() is element1.get_actual(), "Element is found 2 times"


def test_after_refresh(browser):
    browser.open("/disappearing_elements")
    element1 = browser.element("div.example p")
    e_text1 = element1.get_actual().text
    browser.open("http://google.com")
    browser.open("/disappearing_elements")
    e_text2 = element1.get_actual().text
    assert e_text1 == e_text2


def test_not_existing(browser):
    browser.open("/dynamic_loading/1")
    loading = browser.element("div#loading")
    assert not loading.visible
    assert not loading.exists


def test_element_by(browser):
    browser.open("/dynamic_loading/1")
    loading = browser.element(by_css("div#start > button"))
    loading.should(exist)


def test_dynamic_loading(browser):
    browser.open("/dynamic_loading/1")
    start_btn = browser.element("div#start > button")
    finish_txt = browser.element("div#finish")
    loading = browser.element("div#loading")

    finish_txt.should_be(hidden)
    start_btn.click()
    start_btn.should_be(hidden)
    loading.should_be(visible)
    loading.should_be(hidden, timeout=10)
    assert finish_txt.text == "Hello World!"


def test_search_child(browser):
    browser.open("dynamic_loading/1")
    root = browser.element("div#content")
    root.element("div#start").should(exist)


def test_input_text(browser, base_url):
    browser.open("/login")
    form = browser.element("form#login")
    form.element("input#username").text = "tomsmith"
    form.element("input#password").text = "SuperSecretPassword!"
    form.element("button.radius").click()
    assert browser.url == "/secure"
    assert browser.url == f"{base_url}/secure"


def test_browser_from_nested_element(browser):
    browser.open("/large")
    parent = browser.element("div.exapmple")
    child = parent.element("div#siblings > div")
    assert isinstance(child.browser, BrowserSession)


def test_attribute_access(browser):
    browser.open("/forgot_password")
    button = browser.element("#form_submit")

    assert button.id == button.get_attribute("id")
    assert button.type == button.get_attribute("type")


def test_checkboxes(browser):
    browser.open("/checkboxes")
    form = browser.element("form#checkboxes")

    children = form.elements("input")

    ch1 = children[0]
    assert not ch1.selected
    ch1.click()
    assert ch1.selected

    ch2 = children[1]
    assert ch2.selected
    ch2.click()
    assert not ch2.selected


def test_element_hover(browser):
    browser.open("/hovers")
    figures = browser.elements("div.figure")

    def _re_usr_covert(_link: str):
        part1, part2 = _link.split("/")[-2:]
        return f"{part1[:-1]}{part2}"

    for single in figures:  # type: Element
        image = single.element("img")
        caption = single.element("div.figcaption")

        image.hover()
        caption.assure(visible)
        link = caption.element("a")
        assert caption.element("h5").text == f"name: {_re_usr_covert(link.href)}"
        assert link.text == "View profile"


def test_element_parent(browser):
    browser.open("/login")
    username = browser.element("#username")
    div = username.parent
    assert div.tag_name == "div"


def test_clear(browser):
    browser.open("/login")
    username = browser.element("#username")
    username.text = "let me speak"
    username.text = ""
    assert username.text == ""


def test_value(browser):
    browser.open("/dropdown")
    dropdown = browser.element("#dropdown")
    options = dropdown.elements("option")
    assert options[0].value == ""
    assert options[1].value == "1"
    assert options[2].value == "2"


@pytest.fixture
def _prepare_menu(browser):
    browser.open("/jqueryui/menu")
    disabled = browser.element("#ui-id-1")
    enabled = browser.element("#ui-id-2")
    return enabled, disabled


def test_enabled(_prepare_menu):
    enabled, disabled = _prepare_menu
    assert enabled.enabled
    assert not disabled.enabled


def test_disabled(_prepare_menu):
    enabled, disabled = _prepare_menu
    assert disabled.disabled
    assert not enabled.disabled


def test_ancestors(browser):
    browser.open("/login")
    form = browser.element("#login")
    divs = form.ancestors()
    assert len(divs) == 5


def test_ancestors_filter(browser):
    browser.open("/login")
    form = browser.element("#login")
    divs = form.ancestors(lambda e: e.tag_name == "div")
    assert len(divs) == 3


def test_neighbours(browser):
    browser.open("/login")
    inputs = browser.element("#username").neighbours()
    assert len(inputs) == 2


def test_neighbours_filter(browser):
    browser.open("/login")
    username = browser.element("#username")
    not_input = username.neighbours(lambda e: e.tag_name == "label")
    assert len(not_input) == 1
