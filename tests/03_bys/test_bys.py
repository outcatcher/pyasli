from pyasli.bys import *


def test_by_css(random_string):
    actual = by_css(random_string)
    assert By.CSS_SELECTOR, random_string == actual


def test_by_id(random_string):
    actual = by_id(random_string)
    assert By.ID, random_string == actual


def test_by_tag(random_string):
    actual = by_tag(random_string)
    assert By.TAG_NAME, random_string == actual


def test_by_class(random_string):
    actual = by_class(random_string)
    assert By.CLASS_NAME, random_string == actual


def test_by_name(random_string):
    actual = by_name(random_string)
    assert By.NAME, random_string == actual


def test_by_xpath(random_string):
    actual = by_xpath(random_string)
    assert By.XPATH, random_string == actual
