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


# looks stupid, but this way PyCharm won't add brackets automatically
visible = __visible
hidden = __hidden
exist = __exists


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
