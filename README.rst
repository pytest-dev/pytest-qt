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
        qtbot.mouseClick(window.button_greet, QtCore.Qt.LeftButton)
    
        assert window.greet_label.text() == 'Hello!'


.. _PySide: https://pypi.python.org/pypi/PySide
.. _PyQt: http://www.riverbankcomputing.com/software/pyqt
.. _pytest: http://pytest.org

This allows you to test and make sure your view layer is behaving the way you expect after each code change.

.. Using PNG badges because PyPI doesn't support SVG

.. |version| image:: http://img.shields.io/pypi/v/pytest-qt.png
  :target: https://pypi.python.org/pypi/pytest-qt
  
.. |downloads| image:: http://img.shields.io/pypi/dm/pytest-qt.png
  :target: https://pypi.python.org/pypi/pytest-qt
  
.. |ci| image:: http://img.shields.io/travis/nicoddemus/pytest-qt.png
  :target: https://travis-ci.org/nicoddemus/pytest-qt

.. |coverage| image:: http://img.shields.io/coveralls/nicoddemus/pytest-qt.png
  :target: https://coveralls.io/r/nicoddemus/pytest-qt

.. |docs| image:: https://readthedocs.org/projects/pytest-qt/badge/?version=latest
  :target: https://pytest-qt.readthedocs.org

.. |python| image:: https://pypip.in/py_versions/pytest-qt/badge.png
  :target: https://pypi.python.org/pypi/pytest-qt/
  :alt: Supported Python versions

|python| |version| |downloads| |ci| |coverage| |docs|

Requirements
============

Python 2.6 or later, including Python 3+.

Works with either PySide_ or
PyQt_ picking whichever is available on the system, giving
preference to ``PySide`` if both are installed (to force it to use ``PyQt``, set
the environment variable ``PYTEST_QT_FORCE_PYQT=true``).

Documentation
=============

Full documentation and tutorial available at `Read the Docs`_.

.. _Read The Docs: https://pytest-qt.readthedocs.org

Change Log
==========

Please consult the `releases page`_.

.. _releases page: https://github.com/nicoddemus/pytest-qt/releases

Bugs/Requests
=============

Please report any issues or feature requests in the `issue tracker`_.

.. _issue tracker: https://github.com/nicoddemus/pytest-qt/issues

Contributing
============

Contributions are welcome, so feel free to submit a bug or feature
request.

Pull requests are highly appreciated! If you
can, include some tests that exercise the new code or test that a bug has been
fixed, and make sure to include yourself in the contributors list. :)

Contributors
------------

Many thanks to:

- Igor T. Ghisi (`@itghisi <https://github.com/itghisi>`_);
- John David Reaver (`@jdreaver <https://github.com/jdreaver>`_);
- Benjamin Hedrich (`@bh <https://github.com/bh>`_);
- Benjamin Audren (`@baudren <https://github.com/baudren>`_);
- Fabio Zadrozny (`@fabioz <https://github.com/fabioz>`_);

.. _tox: http://tox.readthedocs.org
