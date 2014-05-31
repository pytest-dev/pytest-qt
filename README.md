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

[![version](http://img.shields.io/pypi/v/pytest-qt.svg)](https://crate.io/packages/pytest-qt)
[![downloads](http://img.shields.io/pypi/dm/pytest-qt.svg)](https://crate.io/packages/pytest-qt/)
[![ci](http://img.shields.io/travis/nicoddemus/pytest-qt.svg)](https://travis-ci.org/nicoddemus/pytest-qt)

## Requirements ##

Python 2.6 or later, including Python 3+.

Works with either [PySide](https://pypi.python.org/pypi/PySide) or
[PyQt](http://www.riverbankcomputing.com/software/pyqt), picking one that is available giving
preference to `PySide` if both are installed (to force it to use `PyQt`, set
the environment variable `PYTEST_QT_FORCE_PYQT=true`).

## Documentation ##

Full documentation and tutorial available at [Read the Docs](https://pytest-qt.readthedocs.org/en/latest/).

## Change Log ##

Please consult the [releases page](https://github.com/nicoddemus/pytest-qt/releases).

## Bugs/Requests ##

Please report any issues or feature requests in the [issue tracker](https://github.com/nicoddemus/pytest-qt/issues).
