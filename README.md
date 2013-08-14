# pytest-qt #

pytest-qt is a [pytest](http://pytest.org) plugin that provides fixtures to help 
programmers write tests for [PySide](https://pypi.python.org/pypi/PySide) and [PyQt](http://www.riverbankcomputing.com/software/pyqt)
applications.

The main usage is to use the qtbot fixture, which provides methods to simulate user interaction, like key presses and mouse clicks:

```python
def test_hello(qtbot):
    widget = HelloWidget()
    qtbot.addWidget(widget)
    
    # click in the Greet button and make sure it updates the appropriate label
    qtbot.mouseClick(window.button_greet, QtCore.Qt.LeftButton)
    
    assert window.greet_label.text() == 'Hello!'
```

Full documentation and tutorial available at [Read the Docs](https://pytest-qt.readthedocs.org/en/latest/).

