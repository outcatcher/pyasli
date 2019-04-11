import time

from pyasli.conditions import exist, has_text, text_is, visible


def _try_and_retry(element, fnc):
    assert not fnc(element)
    time.sleep(element.timeout * 1.1)
    assert fnc(element)


def test_exist(element):
    _try_and_retry(element, exist)


def test_visible(element):
    _try_and_retry(element, visible)


def test_has_text(element):
    fnc = has_text("ter")
    _try_and_retry(element, fnc)


def test_text_is(element):
    fnc = text_is("after")
    _try_and_retry(element, fnc)
