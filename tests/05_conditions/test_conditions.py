import time

from pytest import mark

from pyasli.conditions import (
    clickable, disabled, enabled, exist,
    has_text, missing, text_is, visible
)


@mark.parametrize('fnc', [
    enabled,
    exist,
    visible,
    clickable,
    has_text("ter"),
    text_is("after"),
])
def test_conditions(element, fnc):
    assert not fnc(element)
    time.sleep(element.timeout * 1.1)
    assert fnc(element)


@mark.parametrize('fnc', [
    missing,
    disabled,
])
def test_negative_conditions(element, fnc):
    assert fnc(element)
    time.sleep(element.timeout * 1.1)
    assert not fnc(element)
