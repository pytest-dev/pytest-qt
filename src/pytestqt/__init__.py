'''
Introduction
============

pytest-qt is a `pytest`_ that provides fixtures to help programmers write
tests for `PyQt`_ and `PySide`_.

.. _pytest: http://www.pytest.org
.. _PyQt: http://www.riverbankcomputing.com/software/pyqt 
.. _PySide: https://pypi.python.org/pypi/PySide

The main usage is to use the ``qtbot`` fixture, which provides methods to simulate user 
interaction, like key presses and mouse clicks::

    def test_hello(qtbot):
        widget = QtGui.QWidget()
        qtbot.addWidget(widget)
        # test away


QtBot Instances
---------------

.. autoclass:: pytestqt.conftest.QtBot
    :members:

'''