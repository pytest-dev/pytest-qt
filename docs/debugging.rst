Debugging failing tests
=======================

When a GUI-related test fails, it can sometimes be hard to find out where the culprit lies. To aid
with debugging such tests, the ``qtbot`` fixture allows to stop the current
test and to take screenshots of widgets.

Stopping the current test
-------------------------

By calling :meth:`pytestqt.qtbot.QtBot.stop`, the current test gets
interrupted. After closing all visible windows, ``qtbot`` attempts to restore
the previous state and the test continues to run.

.. note::

   If you use Xvfb or the ``offscreen`` platform plugin (e.g. via
   ``QT_QPA_PLATFORM=offscreen``), remember to disable those to see the windows. With the
   `pytest-xvfb <https://github.com/The-Compiler/pytest-xvfb/>`_ plugin, this
   is possible by passing ``--no-xvfb`` to pytest.

Taking screenshots
------------------

.. versionadded:: 4.1

Via :meth:`pytestqt.qtbot.QtBot.screenshot`, a screenshot of a given widget
can be taken. That screenshot is then saved into a temporary directory provided
by pytest. For example, this test:

.. code:: python

    from pytestqt.qt_compat import qt_api


    def test_screenshot(qtbot):
        button = qt_api.QtWidgets.QPushButton()
        button.setText("Hello World!")
        qtbot.add_widget(button)
        path = qtbot.screenshot(button)
        assert False, path  # show the path and fail the test

would result in the following file at a location like
``/tmp/pytest-of-USER/pytest-N/test_screenshot0/screenshot_QPushButton.png``:

.. image:: _static/button.png

The filename is generated based on the following parts:

* ``screenshot``
* The class of the widget (e.g. ``QWidget`` or ``QPushButton``)
* The widget's ``objectName()``, if set
* The given ``suffix``, if passed
* A counter to make the filename unique, if another screenshot already exists
