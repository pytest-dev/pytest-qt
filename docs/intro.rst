=========
pytest-qt
=========

pytest-qt is a `pytest`_ plugin that allows programmers to write tests
for `PyQt5`_, `PyQt6`_, `PySide2`_ and `PySide6`_ applications.

The main usage is to use the ``qtbot`` fixture, responsible for handling ``qApp``
creation as needed, and registering widgets for testing:


.. code-block:: python

    def test_hello(qtbot):
        widget = HelloWidget()
        qtbot.addWidget(widget)

        # Click the greet button and make sure the appropriate label is updated.
        widget.button_greet.click()

        assert widget.greet_label.text() == "Hello!"


.. _PySide2: https://pypi.org/project/PySide2/
.. _PySide6: https://pypi.org/project/PySide6/
.. _PyQt5: https://pypi.org/project/PyQt5/
.. _PyQt6: https://pypi.org/project/PyQt6/
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

``pytest-qt`` requires Python 3.7+.

Works with either PySide6_, PySide2_, PyQt6_ or PyQt5_, picking whichever
is available on the system, giving preference to the first one installed in
this order:

- ``PySide6``
- ``PySide2``
- ``PyQt6``
- ``PyQt5``

To force a particular API, set the configuration variable ``qt_api`` in your ``pytest.ini`` file to
``pyside6``, ``pyside2``, ``pyqt6`` or ``pyqt5``:

.. code-block:: ini

    [pytest]
    qt_api=pyqt5


Alternatively, you can set the ``PYTEST_QT_API`` environment
variable to the same values described above (the environment variable wins over the configuration
if both are set).
