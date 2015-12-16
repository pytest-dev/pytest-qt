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

    def __init__(self, timeout=1000, raising=False):
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
        self._loop.quit()
        self._cleanup()

    def _cleanup(self):
        if self._timer is not None:
            try:
                self._timer.timeout.disconnect(self._quit_loop_by_timeout)
            except (TypeError, RuntimeError):
                # already disconnected by Qt?
                pass
            self._timer.stop()
            self._timer = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
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

    :ivar list args:
        The arguments which were emitted by the signal, or None if the signal
        wasn't emitted at all.

    .. versionadded:: 1.10
       The *args* attribute.

    .. automethod:: wait
    .. automethod:: connect
    """

    def __init__(self, timeout=1000, raising=False):
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
        self.signal_triggered = True
        self.args = list(args)
        self._loop.quit()
        self._cleanup()

    def _cleanup(self):
        super(SignalBlocker, self)._cleanup()
        for signal in self._signals:
            try:
                signal.disconnect(self._quit_loop_by_signal)
            except (TypeError, RuntimeError):  # pragma: no cover
                # already disconnected by Qt?
                pass


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

    def __init__(self, timeout=1000, raising=False):
        super(MultiSignalBlocker, self).__init__(timeout, raising=raising)
        self._signals = {}

    def _add_signal(self, signal):
        """
        Adds the given signal to the list of signals which :meth:`wait()` waits
        for.

        :param signal: QtCore.Signal
        """
        self._signals[signal] = False
        signal.connect(functools.partial(self._signal_emitted, signal))

    def _signal_emitted(self, signal):
        """
        Called when a given signal is emitted.

        If all expected signals have been emitted, quits the event loop and
        marks that we finished because signals.
        """
        self._signals[signal] = True
        if all(self._signals.values()):
            self.signal_triggered = True
            self._loop.quit()


class SignalTimeoutError(Exception):
    """
    .. versionadded:: 1.4

    The exception thrown by :meth:`pytestqt.qtbot.QtBot.waitSignal` if the
    *raising* parameter has been given and there was a timeout.
    """
    pass

