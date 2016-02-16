Introduction
============

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



.. _pytest: http://www.pytest.org
.. _PySide: https://pypi.python.org/pypi/PySide
.. _PyQt: http://www.riverbankcomputing.com/software/pyqt


Requirements
------------

Python 2.7 or later, including Python 3+.

Requires pytest version 2.7 or later.

Works with either ``PySide``, ``PyQt4`` or ``PyQt5``, picking whichever
is available on the system giving preference to the first one installed in
this order:

- ``PySide``
- ``PyQt4``
- ``PyQt5``

To force a particular API, set the environment variable ``PYTEST_QT_API`` to
``pyside``, ``pyqt4``, ``pyqt4v2`` or ``pyqt5``. ``pyqt4v2`` sets the ``PyQt4``
API to `version 2 <version2>`_

.. _version2: http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html

Installation
------------

The package may be installed by running::

   pip install pytest-qt

Or alternatively, download the package from pypi_, extract and execute::

   python setup.py install

.. _pypi: http://pypi.python.org/pypi/pytest-qt/

Both methods will automatically register it for usage in ``py.test``.

Related plugins
---------------

You can also install the `pytest-xvfb`_-plugin to run your tests in `Xvfb`_
which prevents windows popping up on Linux (if Xvfb is installed).

.. _pytest-xvfb: https://github.com/The-Compiler/pytest-xvfb
.. _Xvfb: http://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml

Development
-----------

If you intend to develop ``pytest-qt`` itself, use virtualenv_ to
activate a new fresh environment and execute::

    git clone https://github.com/pytest-dev/pytest-qt.git
    cd pytest-qt
    python setup.py develop
    pip install pyside # or pyqt4/pyqt5


.. _virtualenv: http://virtualenv.readthedocs.org/

Versioning
----------

This projects follows `semantic versioning`_.

.. _`semantic versioning`: http://semver.org/
