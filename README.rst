=========
pytest-qt
=========

pytest-qt is a `pytest`_ plugin that allows programmers to write tests
for `PySide`_ and `PyQt`_ applications.

The main usage is to use the `qtbot` fixture, responsible for handling `qApp` 
creation as needed and provides methods to simulate user interaction, 
like key presses and mouse clicks:


.. code-block:: python

    def test_hello(qtbot):
        widget = HelloWidget()
        qtbot.addWidget(widget)
    
        # click in the Greet button and make sure it updates the appropriate label
        qtbot.mouseClick(widget.button_greet, QtCore.Qt.LeftButton)
    
        assert widget.greet_label.text() == 'Hello!'


.. _PySide: https://pypi.python.org/pypi/PySide
.. _PyQt: http://www.riverbankcomputing.com/software/pyqt
.. _pytest: http://pytest.org

This allows you to test and make sure your view layer is behaving the way you expect after each code change.

.. |version| image:: http://img.shields.io/pypi/v/pytest-qt.svg
  :target: https://pypi.python.org/pypi/pytest-qt
  
.. |downloads| image:: http://img.shields.io/pypi/dm/pytest-qt.svg
  :target: https://pypi.python.org/pypi/pytest-qt
  
.. |travis| image:: https://img.shields.io/travis/pytest-dev/pytest-qt/master.svg
  :target: https://travis-ci.org/pytest-dev/pytest-qt

.. |coverage| image:: http://img.shields.io/coveralls/pytest-dev/pytest-qt.svg
  :target: https://coveralls.io/r/pytest-dev/pytest-qt

.. |docs| image:: https://readthedocs.org/projects/pytest-qt/badge/?version=latest
  :target: https://pytest-qt.readthedocs.io

.. |appveyor| image:: https://img.shields.io/appveyor/ci/pytest-dev/pytest-qt/master.svg
  :target: https://ci.appveyor.com/project/nicoddemus/pytest-qt

.. |python| image:: https://img.shields.io/pypi/pyversions/pytest-qt.svg
  :target: https://pypi.python.org/pypi/pytest-qt/
  :alt: Supported Python versions

|python| |version| |downloads| |travis| |appveyor| |coverage| |docs|


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

Works with either PySide_ or PyQt_ (``PyQt5`` and ``PyQt4``) picking whichever
is available on the system, giving preference to the first one installed in
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

Running tests
-------------

Tests are run using `tox`_. The simplest way to test is with `PySide`_, as it
is available on pip and can be installed by ``tox`` automatically::

    $ tox -e py34-pyside,py27-pyside,docs

If you want to test against `PyQt`_, install it into your global python
installation and use the ``py27-pyqt4``, ``py34-pyqt4`` or ``py34-pyqt5``
testing environments, and ``tox`` will copy the appropriate files into
its virtual environments to ensure isolation.

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

**Powered by**

.. |pycharm| image:: https://www.jetbrains.com/pycharm/docs/logo_pycharm.png
  :target: https://www.jetbrains.com/pycharm
  
.. |pydev| image:: http://www.pydev.org/images/pydev_banner3.png
  :target: https://www.pydev.org
  
|pycharm|  

|pydev|  

.. _tox: https://tox.readthedocs.io
