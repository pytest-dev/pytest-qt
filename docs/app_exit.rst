A note about QApplication.exit()
================================

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
        monkeypatch.setattr(QApplication, 'exit', lambda: exit_calls.append(1))
        button = get_app_exit_button()
        qtbot.click(button)
        assert exit_calls == [1]


Or using the ``mock`` package:

.. code-block:: python

    def test_exit_button(qtbot):
        with mock.patch.object(QApplication, 'exit'):
            button = get_app_exit_button()
            qtbot.click(button)
            assert QApplication.exit.call_count == 1

