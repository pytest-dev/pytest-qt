Testing QApplication
====================

If your tests need access to a full ``QApplication`` instance to e.g. test exit
behavior or custom application classes, you can use the techniques described below:


Testing QApplication.exit()
--------------------------------

Some ``pytest-qt`` features, most notably ``waitSignal`` and ``waitSignals``,
depend on the Qt event loop being active. Calling ``QApplication.exit()``
from a test will cause the main event loop and auxiliary event loops to
exit and all subsequent event loops to fail to start. This is a problem if some
of your tests call an application functionality that calls
``QApplication.exit()``.

One solution is to *monkeypatch* ``QApplication.exit()`` in such tests to ensure
it was called by the application code but without effectively calling it.

For example:

.. code-block:: python

    def test_exit_button(qtbot, monkeypatch):
        exit_calls = []
        monkeypatch.setattr(QApplication, "exit", lambda: exit_calls.append(1))
        button = get_app_exit_button()
        qtbot.click(button)
        assert exit_calls == [1]


Or using the ``mock`` package:

.. code-block:: python

    def test_exit_button(qtbot):
        with mock.patch.object(QApplication, "exit"):
            button = get_app_exit_button()
            qtbot.click(button)
            assert QApplication.exit.call_count == 1


Testing Custom QApplications
----------------------------

It's possible to test custom ``QApplication`` classes, but you need to be
careful to avoid multiple app instances in the same test. Assuming one defines a
custom application like below:

.. code-block:: python

    from PyQt5.QtWidgets import QApplication


    class CustomQApplication(QApplication):
        def __init__(self, *argv):
            super().__init__(*argv)
            self.custom_attr = "xxx"

        def custom_function(self):
            pass


If your tests require access to app-level functions, like
``CustomQApplication.custom_function()``, you can override the built-in
``qapp`` fixture in your ``conftest.py`` to use your own app:

.. code-block:: python

    @pytest.fixture(scope="session")
    def qapp():
        yield CustomQApplication([])

Setting a QApplication name
---------------------------

By default, pytest-qt sets the ``QApplication.applicationName()`` to
``pytest-qt-qapp``. To use a custom name, you can set the ``qt_qapp_name``
option in ``pytest.ini``:

.. code-block:: ini

    [pytest]
    qt_qapp_name = frobnicate-tests
