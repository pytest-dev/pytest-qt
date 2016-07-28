import functools
from pytestqt.qt_compat import qt_api


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
        self._loop = qt_api.QtCore.QEventLoop()
        self.timeout = timeout
        self.signal_triggered = False
        self.raising = raising
        if timeout is None:
            self._timer = None
        else:
            self._timer = qt_api.QtCore.QTimer(self._loop)
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

    def __init__(self, timeout=1000, raising=True, check_params_cb=None):
        super(SignalBlocker, self).__init__(timeout, raising=raising)
        self._signals = []
        self.args = None
        self.check_params_callback = check_params_cb

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
        if self.check_params_callback:
            if not self.check_params_callback(*args):
                return  # parameter check did not pass
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

    def __init__(self, timeout=1000, raising=True, check_params_cbs=None, order="none"):
        super(MultiSignalBlocker, self).__init__(timeout, raising=raising)
        self.order = order
        self.check_params_callbacks = check_params_cbs
        self._signals_emitted = []  # list of booleans, indicates whether the signal was already emitted
        self._signals_map = {}  # maps from a unique Signal to a list of indices where to expect signal instance emits
        self._signals = []  # list of all Signals (for compatibility with _AbstractSignalBlocker)
        self._slots = []  # list of slot functions
        self._signal_expected_index = 0  # only used when forcing order
        self._strict_order_violated = False

    def add_signals(self, signals):
        """
        Adds the given signal to the list of signals which :meth:`wait()` waits
        for.

        :param list signals: list of QtCore.Signal`s
        """
        # determine uniqueness of signals, creating a map that maps from a unique signal to a list of indices
        # (positions) where this signal is expected (in case order matters)
        signals_as_str = [str(signal) for signal in signals]
        signal_str_to_signal = {}  # maps from a signal-string to one of the signal instances (the first one found)
        for index, signal_str in enumerate(signals_as_str):
            signal = signals[index]
            if signal_str not in signal_str_to_signal:
                signal_str_to_signal[signal_str] = signal
                self._signals_map[signal] = [index]  # create a new list
            else:
                # append to existing list
                first_signal_that_occurred = signal_str_to_signal[signal_str]
                self._signals_map[first_signal_that_occurred].append(index)

        for signal in signals:
            self._signals_emitted.append(False)

        for unique_signal in self._signals_map:
            slot = functools.partial(self._signal_emitted, unique_signal)
            self._slots.append(slot)
            unique_signal.connect(slot)
            self._signals.append(unique_signal)

    def _signal_emitted(self, signal, *args):
        """
        Called when a given signal is emitted.

        If all expected signals have been emitted, quits the event loop and
        marks that we finished because signals.
        """
        if self.order == "none":
            # perform the test for every matching index (stop after the first one that matches)
            successfully_emitted = False
            successful_index = -1
            potential_indices = self._get_unemitted_signal_indices(signal)
            for potential_index in potential_indices:
                if self._check_callback(potential_index, *args):
                    successful_index = potential_index
                    successfully_emitted = True
                    break

            if successfully_emitted:
                self._signals_emitted[successful_index] = True
        elif self.order == "simple":
            potential_indices = self._get_unemitted_signal_indices(signal)
            if potential_indices:
                if self._signal_expected_index == potential_indices[0]:
                    if self._check_callback(self._signal_expected_index, *args):
                        self._signals_emitted[self._signal_expected_index] = True
                        self._signal_expected_index += 1
        else:  # self.order == "strict"
            if not self._strict_order_violated:
                # only do the check if the strict order has not been violated yet
                self._strict_order_violated = True  # assume the order has been violated this time
                potential_indices = self._get_unemitted_signal_indices(signal)
                if potential_indices:
                    if self._signal_expected_index == potential_indices[0]:
                        if self._check_callback(self._signal_expected_index, *args):
                            self._signals_emitted[self._signal_expected_index] = True
                            self._signal_expected_index += 1
                            self._strict_order_violated = False  # order has not been violated after all!

        if not self._strict_order_violated and all(self._signals_emitted):
            try:
                self.signal_triggered = True
                self._cleanup()
            finally:
                self._loop.quit()

    def _check_callback(self, index, *args):
        """
        Checks if there's a callback that evaluates the validity of the parameters. Returns False if there is one
        and its evaluation revealed that the parameters were invalid. Returns True otherwise.
        """
        if self.check_params_callbacks:
            callback_func = self.check_params_callbacks[index]
            if callback_func:
                if not callback_func(*args):
                    return False
        return True

    def _get_unemitted_signal_indices(self, signal):
        """Returns the indices for the provided signal for which NO signal instance has been emitted yet."""
        return [index for index in self._signals_map[signal] if self._signals_emitted[index] == False]

    def _cleanup(self):
        super(MultiSignalBlocker, self)._cleanup()
        for i in range(len(self._signals)):
            signal = self._signals[i]
            slot = self._slots[i]
            _silent_disconnect(signal, slot)
        del self._signals_emitted[:]
        self._signals_map.clear()
        del self._slots[:]


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
