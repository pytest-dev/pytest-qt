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

Python 2.7 or later, including Python 3.4+.

Requires pytest version 2.7 or later.

Works with either ``PyQt5``, ``PySide`` or ``PyQt4``, picking whichever
is available on the system giving preference to the first one installed in
this order:

- ``PyQt5``
- ``PySide``
- ``PyQt4``

To force a particular API, set the configuration variable ``qt_api`` in your ``pytest.ini`` file to
``pyqt5``, ``pyside``, ``pyqt4`` or ``pyqt4v2``. ``pyqt4v2`` sets the ``PyQt4``
API to `version 2`_.

.. code-block:: ini

    [pytest]
    qt_api=pyqt5

Alternatively, you can set the ``PYTEST_QT_API`` environment variable to the
same values described above (the environment variable wins over the
configuration if both are set).

From ``pytest-qt`` version 2 the behaviour of ``pyqt4v2`` has changed, as
explained in :doc:`note_pyqt4v2`.

.. _version 2: http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html

Installation
------------

The package may be installed by running::

   pip install pytest-qt

Or alternatively, download the package from pypi_, extract and execute::

   python setup.py install

.. _pypi: http://pypi.python.org/pypi/pytest-qt/

Both methods will automatically register it for usage in ``pytest``.

Development
-----------

If you intend to develop ``pytest-qt`` itself, use virtualenv_ to
activate a new fresh environment and execute::

    git clone https://github.com/pytest-dev/pytest-qt.git
    cd pytest-qt
    pip install -e .  # or python setup.py develop
    pip install pyside # or pyqt4/pyqt5

If you also intend to build the documentation locally, you can make sure to have
all the needed dependences executing::

    pip install -e .[doc]

.. _virtualenv: https://virtualenv.readthedocs.io/

Versioning
----------

This projects follows `semantic versioning`_.

.. _`semantic versioning`: http://semver.org/
