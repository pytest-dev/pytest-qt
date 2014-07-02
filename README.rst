=========
pytest-qt
=========

pytest-qt is a `pytest`_ plugin to allow programmers write tests for `PySide`_ and `PyQt`_ applications.

The main usage is to use the `qtbot` fixture, responsible for handling `qApp` 
creation as needed and provides methods to simulate user interaction, 
like key presses and mouse clicks::


    def test_hello(qtbot):
        widget = HelloWidget()
        qtbot.addWidget(widget)
    
        # click in the Greet button and make sure it updates the appropriate label
        qtbot.mouseClick(window.button_greet, QtCore.Qt.LeftButton)
    
        assert window.greet_label.text() == 'Hello!'


.. _PySide: https://pypi.python.org/pypi/PySide
.. _PyQt: http://www.riverbankcomputing.com/software/pyqt
.. _pytest: http://pytest.org

This allows you to test and make sure your view layer is behaving the way you expect after each code change.

|version| |downloads| |ci|

.. |version| image:: http://img.shields.io/pypi/v/pytest-qt.svg
  :target: https://crate.io/packages/pytest-qt
  
.. |downloads| image:: http://img.shields.io/pypi/dm/pytest-qt.svg
  :target: https://crate.io/packages/pytest-qt
  
.. |ci| image:: http://img.shields.io/travis/nicoddemus/pytest-qt.svg
  :target: https://travis-ci.org/nicoddemus/pytest-qt
  

Requirements
------------

Python 2.6 or later, including Python 3+.

Works with either PySide_ or
PyQt_ picking whichever is available on the system, giving
preference to ``PySide`` if both are installed (to force it to use ``PyQt``, set
the environment variable ``PYTEST_QT_FORCE_PYQT=true``).

Documentation
-------------

Full documentation and tutorial available at `Read the Docs`_.

.. _Read The Docs: https://pytest-qt.readthedocs.org/en/latest/

Change Log
----------

Please consult the `releases page`_.

.. _releases page: https://github.com/nicoddemus/pytest-qt/releases

Bugs/Requests
-------------

Please report any issues or feature requests in the `issue tracker`_.

.. _issue tracker: https://github.com/nicoddemus/pytest-qt/issues
