## Pyasli
[![codecov](https://codecov.io/gh/outcatcher/pyasli/branch/master/graph/badge.svg?token=SH2I5ZB221)](https://codecov.io/gh/outcatcher/pyasli)
![Tests](https://github.com/outcatcher/pyasli/actions/workflows/check.yaml/badge.svg)
![Release](https://github.com/outcatcher/pyasli/actions/workflows/release.yaml/badge.svg)
[![PyPI version](https://img.shields.io/pypi/v/pyasli.svg)](https://pypi.org/project/pyasli/)

### Simple selenium python wrapper

#### There are two ways to use browser:

##### Use default shared driver:

```python
from pyasli.browsers import browser

browser.base_url = "https://the-internet.herokuapp.com"
browser.open("/disappearing_elements")
element1 = browser.element("div.example p")
assert element1.get_actual() is element1.get_actual(), "Element is found 2 times"
```

##### Use exact driver (can be used as context manager):
```python
from pyasli.browsers import BrowserSession

with BrowserSession("chrome", base_url="https://the-internet.herokuapp.com") as browser:
    browser.open("/disappearing_elements")
    element1 = browser.element("div.example p")
    assert element1.get_actual() is element1.get_actual(), "Element is found 2 times"
```

In case `browser_instance` is used as context manager, all browser windows will be closed at
exiting context

----

##### There is no documentation currently. For usage please refer to tests

