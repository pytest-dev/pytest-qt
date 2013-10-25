# pytest-qt #

pytest-qt is a [pytest](http://pytest.org) plugin that provides fixtures to help 
programmers write tests for [PySide](https://pypi.python.org/pypi/PySide) and [PyQt](http://www.riverbankcomputing.com/software/pyqt)
applications.

The main usage is to use the `qtbot` fixture, responsible for handling `qApp` creation as needed and provides methods to 
simulate user interaction, like key presses and mouse clicks:

```python
def test_hello(qtbot):
    widget = HelloWidget()
    qtbot.addWidget(widget)
    
    # click in the Greet button and make sure it updates the appropriate label
    qtbot.mouseClick(window.button_greet, QtCore.Qt.LeftButton)
    
    assert window.greet_label.text() == 'Hello!'
```

This allows you to test and make sure your view layer is behaving the way you expect after each code change.

[![version](https://pypip.in/v/pytest-qt/badge.png)](https://crate.io/packages/pytest-qt)
[![downloads](https://pypip.in/d/pytest-qt/badge.png)](https://crate.io/packages/pytest-qt)
[![ci](https://secure.travis-ci.org/nicoddemus/pytest-qt.png?branch=master)](https://travis-ci.org/nicoddemus/pytest-qt)

## Documentation ##

Full documentation and tutorial available at [Read the Docs](https://pytest-qt.readthedocs.org/en/latest/).

## Bugs/Requests ##

Please report any issues or feature requests in the [issue tracker](https://github.com/nicoddemus/pytest-qt/issues).
