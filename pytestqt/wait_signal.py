import functools
from pytestqt.qt_compat import QtCore


class _AbstractSignalBlocker(object):

    """
    Base class for :class:`SignalBlocker` and :class:`MultiSignalBlocker`.

    Provides :meth:`wait` and a context manager protocol, but no means to add
    new signals and to detect when the signals should be considered "done".
    This needs to be implemented by subclasses.

    Subclasses also need to provide ``self._signals`` which should evaluate to
    ``False`` if no signals were configured.

    """

    def __init__(self, timeout=1000, raising=True):
        self._loop = QtCore.QEventLoop()
        self.timeout = timeout
        self.signal_triggered = False
        self.raising = raising
        if timeout is None:
            self._timer = None
        else:
            self._timer = QtCore.QTimer(self._loop)
            self._timer.setSingleShot(True)
            self._timer.setInterval(timeout)

    def wait(self):
        """
        Waits until either a connected signal is triggered or timeout is reached.

        :raise ValueError: if no signals are connected and timeout is None; in
            this case it would wait forever.
        """
        __tracebackhide__ = True
        if self.signal_triggered:
            return
        if self.timeout is None and not self._signals:
            raise ValueError("No signals or timeout specified.")
        if self._timer is not None:
            self._timer.timeout.connect(self._quit_loop_by_timeout)
            self._timer.start()
        self._loop.exec_()
        if not self.signal_triggered and self.raising:
            raise SignalTimeoutError("Didn't get signal after %sms." %
                                     self.timeout)

    def _quit_loop_by_timeout(self):
        try:
            self._cleanup()
        finally:
            self._loop.quit()

    def _cleanup(self):
        if self._timer is not None:
            _silent_disconnect(self._timer.timeout, self._quit_loop_by_timeout)
            self._timer.stop()
            self._timer = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        __tracebackhide__ = True
        if value is None:
            # only wait if no exception happened inside the "with" block
            self.wait()


class SignalBlocker(_AbstractSignalBlocker):

    """
    Returned by :meth:`pytestqt.qtbot.QtBot.waitSignal` method.

    :ivar int timeout: maximum time to wait for a signal to be triggered. Can
        be changed before :meth:`wait` is called.

    :ivar bool signal_triggered: set to ``True`` if a signal (or all signals in
        case of :class:`MultipleSignalBlocker`) was triggered, or
        ``False`` if timeout was reached instead. Until :meth:`wait` is called,
        this is set to ``None``.

    :ivar bool raising:
        If :class:`SignalTimeoutError` should be raised if a timeout occurred.

        .. note:: contrary to the parameter of same name in
            :meth:`pytestqt.qtbot.QtBot.waitSignal`, this parameter does not
            consider the :ref:`qt_wait_signal_raising`.

    :ivar list args:
        The arguments which were emitted by the signal, or None if the signal
        wasn't emitted at all.

    .. versionadded:: 1.10
       The *args* attribute.

    .. automethod:: wait
    .. automethod:: connect
    """

    def __init__(self, timeout=1000, raising=True):
        super(SignalBlocker, self).__init__(timeout, raising=raising)
        self._signals = []
        self.args = None

    def connect(self, signal):
        """
        Connects to the given signal, making :meth:`wait()` return once
        this signal is emitted.

        More than one signal can be connected, in which case **any** one of
        them will make ``wait()`` return.

        :param signal: QtCore.Signal
        """
        signal.connect(self._quit_loop_by_signal)
        self._signals.append(signal)

    def _quit_loop_by_signal(self, *args):
        """
        quits the event loop and marks that we finished because of a signal.
        """
        try:
            self.signal_triggered = True
            self.args = list(args)
            self._cleanup()
        finally:
            self._loop.quit()

    def _cleanup(self):
        super(SignalBlocker, self)._cleanup()
        for signal in self._signals:
            _silent_disconnect(signal, self._quit_loop_by_signal)
        self._signals = []


class MultiSignalBlocker(_AbstractSignalBlocker):

    """
    Returned by :meth:`pytestqt.qtbot.QtBot.waitSignals` method, blocks until
    all signals connected to it are triggered or the timeout is reached.

    Variables identical to :class:`SignalBlocker`:
        - ``timeout``
        - ``signal_triggered``
        - ``raising``

    .. automethod:: wait
    """

    def __init__(self, timeout=1000, raising=True):
        super(MultiSignalBlocker, self).__init__(timeout, raising=raising)
        self._signals = {}
        self._slots = {}

    def _add_signal(self, signal):
        """
        Adds the given signal to the list of signals which :meth:`wait()` waits
        for.

        :param signal: QtCore.Signal
        """
        self._signals[signal] = False
        slot = functools.partial(self._signal_emitted, signal)
        self._slots[signal] = slot
        signal.connect(slot)

    def _signal_emitted(self, signal):
        """
        Called when a given signal is emitted.

        If all expected signals have been emitted, quits the event loop and
        marks that we finished because signals.
        """
        self._signals[signal] = True
        if all(self._signals.values()):
            try:
                self.signal_triggered = True
                self._cleanup()
            finally:
                self._loop.quit()

    def _cleanup(self):
        super(MultiSignalBlocker, self)._cleanup()
        for signal, slot in self._slots.items():
            _silent_disconnect(signal, slot)
        self._signals.clear()
        self._slots.clear()


class SignalEmittedSpy(object):

    """
    .. versionadded:: 1.11

    An object which checks if a given signal has ever been emitted.

    Intended to be used as a context manager.
    """

    def __init__(self, signal):
        self.signal = signal
        self.emitted = False
        self.args = None

    def slot(self, *args):
        self.emitted = True
        self.args = args

    def __enter__(self):
        self.signal.connect(self.slot)

    def __exit__(self, type, value, traceback):
        self.signal.disconnect(self.slot)

    def assert_not_emitted(self):
        if self.emitted:
            if self.args:
                raise SignalEmittedError("Signal %r unexpectedly emitted with "
                                         "arguments %r" %
                                         (self.signal, list(self.args)))
            else:
                raise SignalEmittedError("Signal %r unexpectedly emitted" %
                                         (self.signal,))


class SignalTimeoutError(Exception):
    """
    .. versionadded:: 1.4

    The exception thrown by :meth:`pytestqt.qtbot.QtBot.waitSignal` if the
    *raising* parameter has been given and there was a timeout.
    """
    pass


class SignalEmittedError(Exception):
    """
    .. versionadded:: 1.11

    The exception thrown by :meth:`pytestqt.qtbot.QtBot.assertNotEmitted` if a
    signal was emitted unexpectedly.
    """
    pass


def _silent_disconnect(signal, slot):
    """Disconnects a signal from a slot, ignoring errors. Sometimes
    Qt might disconnect a signal automatically for unknown reasons.
    """
    try:
        signal.disconnect(slot)
    except (TypeError, RuntimeError):  # pragma: no cover
        pass
