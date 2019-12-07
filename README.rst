=========
pytest-qt
=========

pytest-qt is a `pytest`_ plugin that allows programmers to write tests
for `PySide`_, ``PySide2`` and `PyQt`_ applications.

The main usage is to use the ``qtbot`` fixture, responsible for handling ``qApp``
creation as needed and provides methods to simulate user interaction,
like key presses and mouse clicks:


.. code-block:: python

    def test_hello(qtbot):
        widget = HelloWidget()
        qtbot.addWidget(widget)

        # click in the Greet button and make sure it updates the appropriate label
        qtbot.mouseClick(widget.button_greet, QtCore.Qt.LeftButton)

        assert widget.greet_label.text() == "Hello!"


.. _PySide: https://pypi.python.org/pypi/PySide
.. _PySide2: https://wiki.qt.io/PySide2
.. _PyQt: http://www.riverbankcomputing.com/software/pyqt
.. _pytest: http://pytest.org

This allows you to test and make sure your view layer is behaving the way you expect after each code change.

.. |version| image:: http://img.shields.io/pypi/v/pytest-qt.svg
  :target: https://pypi.python.org/pypi/pytest-qt

.. |conda-forge| image:: https://img.shields.io/conda/vn/conda-forge/pytest-qt.svg
    :target: https://anaconda.org/conda-forge/pytest-qt

.. |ci| image:: https://github.com/pytest-dev/pytest-qt/workflows/build/badge.svg
  :target: https://github.com/pytest-dev/pytest-qt/actions

.. |coverage| image:: http://img.shields.io/coveralls/pytest-dev/pytest-qt.svg
  :target: https://coveralls.io/r/pytest-dev/pytest-qt

.. |docs| image:: https://readthedocs.org/projects/pytest-qt/badge/?version=latest
  :target: https://pytest-qt.readthedocs.io

.. |python| image:: https://img.shields.io/pypi/pyversions/pytest-qt.svg
  :target: https://pypi.python.org/pypi/pytest-qt/
  :alt: Supported Python versions

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
  :target: https://github.com/ambv/black

|python| |version| |conda-forge| |ci| |coverage| |docs| |black|


Features
========

- `qtbot`_ fixture to simulate user interaction with ``Qt`` widgets.
- `Automatic capture`_ of ``qDebug``, ``qWarning`` and ``qCritical`` messages;
- waitSignal_ and waitSignals_ functions to block test execution until specific
  signals are emitted.
- `Exceptions in virtual methods and slots`_ are automatically captured and
  fail tests accordingly.

.. _qtbot: https://pytest-qt.readthedocs.io/en/latest/reference.html#module-pytestqt.qtbot
.. _Automatic capture: https://pytest-qt.readthedocs.io/en/latest/logging.html
.. _waitSignal: https://pytest-qt.readthedocs.io/en/latest/signals.html
.. _waitSignals: https://pytest-qt.readthedocs.io/en/latest/signals.html
.. _Exceptions in virtual methods and slots: https://pytest-qt.readthedocs.io/en/latest/virtual_methods.html

Requirements
============

Works with either PySide_, PySide2_ or PyQt_ (``PyQt5`` and ``PyQt4``) picking whichever
is available on the system, giving preference to the first one installed in
this order:

- ``PySide2``
- ``PyQt5``
- ``PySide``
- ``PyQt4``

To force a particular API, set the configuration variable ``qt_api`` in your ``pytest.ini`` file to
``pyqt5``, ``pyside``, ``pyside2``, ``pyqt4`` or ``pyqt4v2``. ``pyqt4v2`` sets the ``PyQt4``
API to `version 2`_.

.. code-block:: ini

    [pytest]
    qt_api=pyqt5


Alternatively, you can set the ``PYTEST_QT_API`` environment
variable to the same values described above (the environment variable wins over the configuration
if both are set).

.. _version 2: http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html


Documentation
=============

Full documentation and tutorial available at `Read the Docs`_.

.. _Read The Docs: https://pytest-qt.readthedocs.io

Change Log
==========

Please consult the `changelog page`_.

.. _changelog page: https://pytest-qt.readthedocs.io/en/latest/changelog.html

Bugs/Requests
=============

Please report any issues or feature requests in the `issue tracker`_.

.. _issue tracker: https://github.com/pytest-dev/pytest-qt/issues

Contributing
============

Contributions are welcome, so feel free to submit a bug or feature
request.

Pull requests are highly appreciated! If you
can, include some tests that exercise the new code or test that a bug has been
fixed, and make sure to include yourself in the contributors list. :)

To prepare your environment, create a virtual environment and install ``pytest-qt`` in editable mode with ``dev``
extras::

    $ pip install --editable .[dev]

After that install ``pre-commit`` for pre-commit checks::

    $ pre-commit install

Running tests
-------------

Tests are run using `tox`_. It is recommended to develop locally on Python 3 because
``PyQt5`` and ``PySide2`` are easily installable using ``pip``::

    $ tox -e py37-pyside2,py37-pyqt5

``pytest-qt`` is formatted using `black <https://github.com/ambv/black>`_ and uses
`pre-commit <https://github.com/pre-commit/pre-commit>`_ for linting checks before commits. You
can install ``pre-commit`` locally with::

    $ pip install pre-commit
    $ pre-commit install


Contributors
------------

Many thanks to:

- Igor T. Ghisi (`@itghisi <https://github.com/itghisi>`_);
- John David Reaver (`@jdreaver <https://github.com/jdreaver>`_);
- Benjamin Hedrich (`@bh <https://github.com/bh>`_);
- Benjamin Audren (`@baudren <https://github.com/baudren>`_);
- Fabio Zadrozny (`@fabioz <https://github.com/fabioz>`_);
- Datalyze Solutions (`@datalyze-solutions <https://github.com/datalyze-solutions>`_);
- Florian Bruhin (`@The-Compiler <https://github.com/The-Compiler>`_);
- Guilherme Quentel Melo (`@gqmelo <https://github.com/gqmelo>`_);
- Francesco Montesano (`@montefra <https://github.com/montefra>`_);
- Roman Yurchak (`@rth <https://github.com/rth>`_)

**Powered by**

.. |pycharm| image:: https://www.jetbrains.com/pycharm/docs/logo_pycharm.png
  :target: https://www.jetbrains.com/pycharm

.. |pydev| image:: http://www.pydev.org/images/pydev_banner3.png
  :target: https://www.pydev.org

|pycharm|

|pydev|

.. _tox: https://tox.readthedocs.io
