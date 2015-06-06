Introduction
============

.. automodule:: pytestqt

Requirements
------------

Python 2.6 or later, including Python 3+.

Tested with pytest version 2.5.2.

Works with either ``PySide``, ``PyQt4`` or ``PyQt5``, picking whichever
is available on the system giving preference to the first one installed in
this order:

- ``PySide``
- ``PyQt4``
- ``PyQt5``

To force a particular API, set the environment variable ``PYTEST_QT_API`` to
``pyside``, ``pyqt4`` or ``pyqt5``.

Installation
------------

The package may be installed by running::

   pip install pytest-qt

Or alternatively, download the package from pypi_, extract and execute::

   python setup.py install

.. _pypi: http://pypi.python.org/pypi/pytest-qt/

Both methods will automatically register it for usage in ``py.test``.

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
