"""List of helpers with commonly used conditions"""

from pyasli.elements.elements import Element, ElementCondition

# pylint: disable=invalid-name

def __visible(element: Element) -> bool:
    """Element is visible"""
    return element.visible


def __hidden(element: Element) -> bool:
    """Element is hidden"""
    return element.hidden


def __exists(element: Element) -> bool:
    """Element exists"""
    return element.exists


def __enabled(element: Element):
    """Condition to check if element is not disabled"""
    return element.enabled


def __disabled(element: Element):
    """Condition to check if element is disabled"""
    return element.disabled


def __missing(element: Element):
    """Condition to check if element is missing from DOM

    Antonym to `exists`
    """
    return not element.exists


def __clickable(element: Element) -> bool:
    """Check if element available for interaction"""
    return __visible(element) and __enabled(element)


def __rename(fnc, name):
    fnc.__name__ = name
    return fnc


# looks stupid, but this way PyCharm won't add brackets automatically
visible = __rename(__visible, "visible")
hidden = __rename(__hidden, "hidden")
exist = __rename(__exists, "exist")
missing = __rename(__missing, "missing")
enabled = __rename(__enabled, "enabled")
disabled = __rename(__disabled, "disabled")
clickable = __rename(__clickable, "clickable")


def text_is(text: str) -> ElementCondition:
    """Element text is"""

    def _text_is(element):
        return element.text == text

    _text_is.__name__ = f"text_is '{text}'"  # condition name is used in repr
    return _text_is


def have_text(text: str) -> ElementCondition:
    """Contains text"""

    def _has_text(element):
        return text in element.text

    _has_text.__name__ = f"has_text '{text}'"
    return _has_text


has_text = have_text  # backward compatibility
