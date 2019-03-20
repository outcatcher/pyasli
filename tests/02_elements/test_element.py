"""Element wrapper tests"""
from pyasli.browser import BrowserSession
from pyasli.bys import by_css


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
    assert not loading.exists()
    assert not loading.is_visible()


def test_element_by(browser):
    browser.open("/dynamic_loading/1")
    loading = browser.element(by_css("div#start > button"))
    loading.should.exist()


def test_dynamic_loading(browser):
    browser.open("/dynamic_loading/1")
    start_btn = browser.element("div#start > button")
    finish_txt = browser.element("div#finish")
    loading = browser.element("div#loading")

    finish_txt.should_be.hidden()
    start_btn.click()
    start_btn.should_be.hidden()
    loading.should_be.visible()
    loading.should_be.hidden(timeout=10)
    assert finish_txt.text == "Hello World!"


def test_search_child(browser):
    browser.open("dynamic_loading/1")
    root = browser.element("div#content")
    root.element("div#start").should.exist()


def test_input_text(browser):
    browser.open("/login")
    form = browser.element("form#login")
    form.element("input#username").text = "tomsmith"
    form.element("input#password").text = "SuperSecretPassword!"
    form.element("button.radius").click()
    assert browser.url == "/secure"
    assert browser.url == "http://the-internet.herokuapp.com/secure"


def test_browser_from_nested_element(browser):
    browser.open("/large")
    parent = browser.element("div.exapmple")
    child = parent.element("div#siblings > div")
    assert isinstance(child.browser, BrowserSession)
