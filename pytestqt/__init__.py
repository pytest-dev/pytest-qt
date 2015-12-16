'''
`pytest-qt` is a pytest_ plugin that provides fixtures to help programmers write tests for
PySide_ and PyQt_.

The main usage is to use the ``qtbot`` fixture, which provides methods to simulate user 
interaction, like key presses and mouse clicks::

    def test_hello(qtbot):
        widget = HelloWidget()
        qtbot.addWidget(widget)
        
        # click in the Greet button and make sure it updates the appropriate label
        qtbot.mouseClick(window.button_greet, QtCore.Qt.LeftButton)
        
        assert window.greet_label.text() == 'Hello!'


.. .. literalinclude:: ../src/pytestqt/_tests/test_basics.py
..    :language: python
..    :start-after: # create test widget


.. _pytest: http://www.pytest.org
.. _PySide: https://pypi.python.org/pypi/PySide
.. _PyQt: http://www.riverbankcomputing.com/software/pyqt

'''

version = '1.10.0'
__version__ = version
