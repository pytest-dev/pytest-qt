waitSignal: Waiting for threads, processes, etc.
================================================

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
            # Test will block at this point until either the "finished" or the
            # "failed" signal is emitted. If 10 seconds passed without a signal,
            # SignalTimeoutError will be raised.

        assert_application_results(app)



raising parameter
-----------------

.. versionadded:: 1.4
.. versionchanged:: 2.0                  

You can pass ``raising=False`` to avoid raising a
:class:`qtbot.SignalTimeoutError <SignalTimeoutError>` if the timeout is
reached before the signal is triggered:

.. code-block:: python

    def test_long_computation(qtbot):
        ...
        with qtbot.waitSignal(app.worker.finished, raising=False) as blocker:
            app.worker.start()

        assert_application_results(app)

        # qtbot.SignalTimeoutError is not raised, but you can still manually
        # check whether the signal was triggered:
        assert blocker.signal_triggered, "process timed-out"

.. _qt_wait_signal_raising:

qt_wait_signal_raising ini option
---------------------------------

.. versionadded:: 1.11
.. versionchanged:: 2.0                  

The ``qt_wait_signal_raising`` ini option can be used to override the default
value of the ``raising`` parameter of the ``qtbot.waitSignal`` and
``qtbot.waitSignals`` functions when omitted:

.. code-block:: ini

    [pytest]
    qt_wait_signal_raising = false

Calls which explicitly pass the ``raising`` parameter are not affected.


check_params_cb parameter
-------------------------

.. versionadded:: 2.0

If the signal has parameters you want to compare with expected values, you can pass 
``check_params_cb=some_callable`` that compares the provided signal parameters to some expected parameters.
It has to match the signature of ``signal`` (just like a slot function would) and return ``True`` if
parameters match, ``False`` otherwise.

.. code-block:: python

    def test_status_100(status):
        """Return true if status has reached 100%."""
        return status == 100

    def test_status_complete(qtbot):
        app = Application()
        
        # the following raises if the worker's status signal (which has an int parameter) wasn't raised 
        # with value=100 within the default timeout
        with qtbot.waitSignal(app.worker.status, raising=True, check_params_cb=test_status_100) as blocker:
            app.worker.start()


Getting arguments of the emitted signal
---------------------------------------

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

Getting all arguments of non-matching arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 2.1

When using the ``check_params_cb`` parameter, it may happen that the provided signal is received multiple times with
different parameter values, which may or may not match the requirements of the callback.
``all_args`` then contains the list of signal parameters (as tuple) in the order they were received.


waitSignals
-----------

.. versionadded:: 1.4

If you have to wait until **all** signals in a list are triggered, use
:meth:`qtbot.waitSignals <pytestqt.plugin.QtBot.waitSignals>`, which receives
a list of signals instead of a single signal. As with
:meth:`qtbot.waitSignal <pytestqt.plugin.QtBot.waitSignal>`, it also supports
the ``raising`` parameter::

    def test_workers(qtbot):
        workers = spawn_workers()
        with qtbot.waitSignals([w.finished for w in workers]):
            for w in workers:
                w.start()

        # this will be reached after all workers emit their "finished"
        # signal or a qtbot.SignalTimeoutError will be raised
        assert_application_results(app)

check_params_cbs parameter
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 2.0

Corresponding to the ``check_params_cb`` parameter of ``waitSignal`` you can use the ``check_params_cbs``
parameter to check whether one or more of the provided signals are emitted with expected parameters.
Provide a list of callables, each matching the signature of the corresponding signal
in ``signals`` (just like a slot function would). Like for ``waitSignal``, each callable has to
return ``True`` if parameters match, ``False`` otherwise.
Instead of a specific callable, ``None`` can be provided, to disable parameter checking for the
corresponding signal.
If the number of callbacks doesn't match the number of signals ``ValueError`` will be raised.

The following example shows that the ``app.worker.status`` signal has to be emitted with values 50 and
100, and the ``app.worker.finished`` signal has to be emitted too (for which no signal parameter
evaluation takes place).


.. code-block:: python

    def test_status_100(status):
        """Return true if status has reached 100%."""
        return status == 100

    def test_status_50(status):
        """Return true if status has reached 50%."""
        return status == 50

    def test_status_complete(qtbot):
        app = Application()
        
        signals = [app.worker.status, app.worker.status, app.worker.finished]
        callbacks = [test_status_50, test_status_100, None]
        with qtbot.waitSignals(signals, raising=True, check_params_cbs=callbacks) as blocker:
            app.worker.start()


order parameter
^^^^^^^^^^^^^^^

.. versionadded:: 2.0

By default a test using ``qtbot.waitSignals`` completes successfully if *all* signals in ``signals`` 
are emitted, irrespective of their exact order. The ``order`` parameter can be set to ``"strict"``
to enforce strict signal order.
Exemplary, this means that ``blocker.signal_triggered`` will be ``False`` if ``waitSignals`` expects 
the signals ``[a, b]`` but the sender emitted signals ``[a, a, b]``.

.. note::

    The tested component can still emit signals unknown to the blocker. E.g.
    ``blocker.waitSignals([a, b], raising=True, order="strict")`` won't raise if the signal-sender
    emits signals ``[a, c, b]``, as ``c`` is not part of the observed signals.

A third option is to set ``order="simple"`` which is like "strict", but signals may be emitted
in-between the provided ones, e.g. if the expected signals are ``[a, b, c]`` and the sender 
actually emits ``[a, a, b, a, c]``, the test completes successfully (it would fail with ``order="strict"``).

Getting emitted signals and arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 2.1

To determine which of the expected signals were emitted during a ``wait()`` you can use
``blocker.all_signals_and_args`` which contains a list of
:class:`wait_signal.SignalAndArgs <SignalAndArgs>` objects, indicating the signals (and their arguments)
in the order they were received.


Making sure a given signal is not emitted
-----------------------------------------

.. versionadded:: 1.11

If you want to ensure a signal is **not** emitted in a given block of code, use
the :meth:`qtbot.assertNotEmitted <pytestqt.plugin.QtBot.assertNotEmitted>`
context manager:

.. code-block:: python

    def test_no_error(qtbot):
        ...
        with qtbot.assertNotEmitted(app.worker.error):
            app.worker.start()
