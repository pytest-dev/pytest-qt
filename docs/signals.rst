Waiting for threads, processes, etc.
====================================

.. versionadded:: 1.2

If your program has long running computations running in other threads or
processes, you can use :meth:`qtbot.waitSignal <pytestqt.plugin.QtBot.waitSignal>`
to block a test until a signal is emitted (such as ``QThread.finished``) or a
timeout is reached. This makes it easy to write tests that wait until a
computation running in another thread or process is completed before
ensuring the results are correct::

    def test_long_computation(qtbot):
        app = Application()

        # Watch for the app.worker.finished signal, then start the worker.
        with qtbot.waitSignal(app.worker.finished, timeout=10000) as blocker:
            blocker.connect(app.worker.failed)  # Can add other signals to blocker
            app.worker.start()
            # Test will block at this point until signal is emitted or
            # 10 seconds has elapsed

        assert blocker.signal_triggered, "process timed-out"
        assert_application_results(app)



**raising parameter**

.. versionadded:: 1.4

You can pass ``raising=True`` to raise a
:class:`qtbot.SignalTimeoutError <SignalTimeoutError>` if the timeout is
reached before the signal is triggered:

.. code-block:: python

    def test_long_computation(qtbot):
        ...
        with qtbot.waitSignal(app.worker.finished, raising=True) as blocker:
            app.worker.start()
        # if timeout is reached, qtbot.SignalTimeoutError will be raised at this point
        assert_application_results(app)


.. versionadded:: 1.11

The ``qt_wait_signal_raising`` ini option can be used to override the default
value of the ``raising`` parameter of the ``qtbot.waitSignal`` and
``qtbot.waitSignals`` functions when omitted:

.. code-block:: ini

    [pytest]
    qt_wait_signal_raising = true

Calls which explicitly pass the ``raising`` parameter are not affected.


**Getting arguments of the emitted signal**

.. versionadded:: 1.10

The arguments emitted with the signal are available as the ``args`` attribute
of the blocker:


.. code-block:: python

    def test_signal(qtbot):
        ...
        with qtbot.waitSignal(app.got_cmd) as blocker:
            app.listen()
        assert blocker.args == ['test']


Signals without arguments will set ``args`` to an empty list. If the time out
is reached instead, ``args`` will be ``None``.

**waitSignals**

.. versionadded:: 1.4

If you have to wait until **all** signals in a list are triggered, use
:meth:`qtbot.waitSignals <pytestqt.plugin.QtBot.waitSignals>`, which receives
a list of signals instead of a single signal. As with
:meth:`qtbot.waitSignal <pytestqt.plugin.QtBot.waitSignal>`, it also supports
the new ``raising`` parameter::

    def test_workers(qtbot):
        workers = spawn_workers()
        with qtbot.waitSignal([w.finished for w in workers], raising=True):
            for w in workers:
                w.start()

        # this will be reached after all workers emit their "finished"
        # signal or a qtbot.SignalTimeoutError will be raised
        assert_application_results(app)

**Making sure a given signal is not emitted**

.. versionadded:: 1.11

If you want to ensure a signal is **not** emitted in a given block of code, use
the :meth:`qtbot.assertNotEmitted <pytestqt.plugin.QtBot.assertNotEmitted>`
context manager:

.. code-block:: python

    def test_no_error(qtbot):
        ...
        with qtbot.assertNotEmitted(app.worker.error):
            app.worker.start()
