waitCallback: Waiting for methods taking a callback
===================================================

.. versionadded:: 3.1

Some methods in Qt (especially ``QtWebEngine``) take a callback as argument,
which gets called by Qt once a given operation is done.

To test such code, you can use :meth:`qtbot.waitCallback <pytestqt.plugin.QtBot.waitCallback>`
which waits until the callback has been called or a timeout is reached.

The ``qtbot.waitCallback()`` method returns a callback which is callable
directly.

For example:

.. code-block:: python

   def test_js(qtbot):
       page = QWebEnginePage()
       with qtbot.waitCallback() as cb:
           page.runJavaScript("1 + 1", cb)
       # After callback

Anything following the ``with`` block will be run only after the callback has been called.

If the callback doesn't get called during the given timeout,
:class:`qtbot.TimeoutError <TimeoutError>` is raised. If it is called more than once,
:class:`qtbot.CallbackCalledTwiceError <CallbackCalledTwiceError>` is raised.

raising parameter
-----------------

Similarly to ``qtbot.waitSignal``, you can pass a ``raising=False`` parameter
(or set the ``qt_default_raising`` ini option) to avoid raising an exception on
timeouts. See :doc:`signals` for details.

Getting arguments the callback was called with
----------------------------------------------

After the callback is called, the arguments and keyword arguments passed to it
are available via ``.args`` (as a list) and ``.kwargs`` (as a dict),
respectively.

In the example above, we could check the result via:

.. code-block:: python

       assert cb.args == [2]
       assert cb.kwargs == {}

Instead of checking the arguments by hand, you can use ``.assert_called_with()``
to make sure the callback was called with the given arguments:

.. code-block:: python

       cb.assert_called_with(2)
