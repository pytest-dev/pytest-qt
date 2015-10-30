import functools
import time
import sys

import pytest

from pytestqt.qt_compat import QtCore, Signal, QT_API


def test_signal_blocker_exception(qtbot):
    """
    Make sure waitSignal without signals and timeout doesn't hang, but raises
    ValueError instead.
    """
    with pytest.raises(ValueError):
        qtbot.waitSignal(None, None).wait()
    with pytest.raises(ValueError):
        qtbot.waitSignals([], None).wait()


def explicit_wait(qtbot, signal, timeout, multiple, raising, should_raise):
    """
    Explicit wait for the signal using blocker API.
    """
    func = qtbot.waitSignals if multiple else qtbot.waitSignal
    blocker = func(signal, timeout, raising=raising)
    assert not blocker.signal_triggered
    if should_raise:
        with pytest.raises(qtbot.SignalTimeoutError):
            blocker.wait()
    else:
        blocker.wait()
    return blocker


def context_manager_wait(qtbot, signal, timeout, multiple, raising,
                         should_raise):
    """
    Waiting for signal using context manager API.
    """
    func = qtbot.waitSignals if multiple else qtbot.waitSignal
    if should_raise:
        with pytest.raises(qtbot.SignalTimeoutError):
            with func(signal, timeout, raising=raising) as blocker:
                pass
    else:
        with func(signal, timeout, raising=raising) as blocker:
            pass
    return blocker


def build_signal_tests_variants(params):
    """
    Helper function to use with pytest's parametrize, to generate additional
    combinations of parameters in a parametrize call:
    - explicit wait and context-manager wait
    - raising True and False (since we check for the correct behavior inside
      each test).
    """
    result = []
    for param in params:
        for wait_function in (explicit_wait, context_manager_wait):
            for raising in (True, False):
                result.append(param + (wait_function, raising))
    return result


@pytest.mark.parametrize(
    ('delay', 'timeout', 'expected_signal_triggered',
     'wait_function', 'raising'),
    build_signal_tests_variants([
        # delay, timeout, expected_signal_triggered
        (200, None, True),
        (200, 400, True),
        (400, 200, False),
    ])
)
def test_signal_triggered(qtbot, timer, stop_watch, wait_function, delay,
                          timeout, expected_signal_triggered, raising,
                          signaller):
    """
    Testing for a signal in different conditions, ensuring we are obtaining
    the expected results.
    """
    timer.single_shot(signaller.signal, delay)

    should_raise = raising and not expected_signal_triggered

    stop_watch.start()
    blocker = wait_function(qtbot, signaller.signal, timeout, raising=raising,
                            should_raise=should_raise, multiple=False)

    # ensure that either signal was triggered or timeout occurred
    assert blocker.signal_triggered == expected_signal_triggered

    stop_watch.check(timeout, delay)


@pytest.mark.parametrize(
    ('delay_1', 'delay_2', 'timeout', 'expected_signal_triggered',
     'wait_function', 'raising'),
    build_signal_tests_variants([
        # delay1, delay2, timeout, expected_signal_triggered
        (200, 300, 400, True),
        (300, 200, 400, True),
        (200, 300, None, True),
        (400, 400, 200, False),
        (200, 400, 300, False),
        (400, 200, 200, False),
        (200, 1000, 400, False),
    ])
)
def test_signal_triggered_multiple(qtbot, timer, stop_watch, wait_function,
                                   delay_1, delay_2, timeout, signaller,
                                   expected_signal_triggered, raising):
    """
    Testing for a signal in different conditions, ensuring we are obtaining
    the expected results.
    """
    timer.single_shot(signaller.signal, delay_1)
    timer.single_shot(signaller.signal_2, delay_2)

    should_raise = raising and not expected_signal_triggered

    stop_watch.start()
    blocker = wait_function(qtbot, [signaller.signal, signaller.signal_2],
                            timeout, multiple=True, raising=raising,
                            should_raise=should_raise)

    # ensure that either signal was triggered or timeout occurred
    assert blocker.signal_triggered == expected_signal_triggered

    stop_watch.check(timeout, delay_1, delay_2)


def test_explicit_emit(qtbot, signaller):
    """
    Make sure an explicit emit() inside a waitSignal block works.
    """
    with qtbot.waitSignal(signaller.signal, timeout=5000) as waiting:
        signaller.signal.emit()

    assert waiting.signal_triggered


def test_explicit_emit_multiple(qtbot, signaller):
    """
    Make sure an explicit emit() inside a waitSignal block works.
    """
    with qtbot.waitSignals([signaller.signal, signaller.signal_2],
                           timeout=5000) as waiting:
        signaller.signal.emit()
        signaller.signal_2.emit()

    assert waiting.signal_triggered


@pytest.fixture
def signaller(timer):
    """
    Fixture that provides an object with to signals that can be emitted by
    tests.

    .. note:: we depend on "timer" fixture to ensure that signals emitted
    with "timer" are disconnected before the Signaller() object is destroyed.
    This was the reason for some random crashes experienced on Windows (#80).
    """
    class Signaller(QtCore.QObject):
        signal = Signal()
        signal_2 = Signal()

    assert timer

    return Signaller()


@pytest.yield_fixture
def timer():
    """
    Fixture that provides a callback with signature: (signal, delay) that
    triggers that signal once after the given delay in ms.

    The fixture is responsible for cleaning up after the timers.
    """

    class Timer(QtCore.QObject):

        def __init__(self):
            QtCore.QObject.__init__(self)
            self.timers_and_slots = []

        def shutdown(self):
            for t, slot in self.timers_and_slots:
                t.stop()
                t.timeout.disconnect(slot)
            self.timers_and_slots[:] = []

        def single_shot(self, signal, delay):
            t = QtCore.QTimer(self)
            t.setSingleShot(True)
            slot = functools.partial(self._emit, signal)
            t.timeout.connect(slot)
            t.start(delay)
            self.timers_and_slots.append((t, slot))

        def _emit(self, signal):
            signal.emit()

    timer = Timer()
    yield timer
    timer.shutdown()


@pytest.fixture
def stop_watch():
    """
    Fixture that makes it easier for tests to ensure signals emitted and
    timeouts are being respected in waitSignal and waitSignals tests.
    """
    # time.clock() is more accurate on Windows
    get_time = time.clock if sys.platform.startswith('win') else time.time

    class StopWatch:

        def __init__(self):
            self._start_time = None
            self.elapsed = None

        def start(self):
            self._start_time = get_time()

        def stop(self):
            self.elapsed = (get_time() - self._start_time) * 1000.0

        def check(self, timeout, *delays):
            """
            Make sure either timeout (if given) or at most of the given
            delays used to trigger a signal has passed.
            """
            self.stop()
            if timeout is None:
                timeout = max(delays) * 1.35  # 35% tolerance
            max_wait_ms = max(delays + (timeout,))
            assert self.elapsed < max_wait_ms

    return StopWatch()


@pytest.mark.parametrize('multiple', [True, False])
@pytest.mark.parametrize('raising', [True, False])
def test_wait_signals_handles_exceptions(qtbot, multiple, raising, signaller):
    """
    Make sure waitSignal handles exceptions correctly.
    """
    class TestException(Exception):
        pass

    if multiple:
        func = qtbot.waitSignals
        arg = [signaller.signal, signaller.signal_2]
    else:
        func = qtbot.waitSignal
        arg = signaller.signal

    with pytest.raises(TestException):
        with func(arg, timeout=10, raising=raising):
            raise TestException


@pytest.mark.parametrize('multiple', [True, False])
@pytest.mark.parametrize('do_timeout', [True, False])
def test_wait_twice(qtbot, timer, multiple, do_timeout, signaller):
    """
    https://github.com/pytest-dev/pytest-qt/issues/69
    """
    if multiple:
        func = qtbot.waitSignals
        arg = [signaller.signal]
    else:
        func = qtbot.waitSignal
        arg = signaller.signal

    if do_timeout:
        with func(arg, timeout=100):
            timer.single_shot(signaller.signal, 200)
        with func(arg, timeout=100):
            timer.single_shot(signaller.signal, 200)
    else:
        with func(arg):
            signaller.signal.emit()
        with func(arg):
            signaller.signal.emit()


@pytest.mark.skipif(QT_API == 'pyside', reason='test crashes PySide')
def test_destroyed(qtbot):
    """Test that waitSignal works with the destroyed signal (#82).

    For some reason, this crashes PySide although it seems perfectly fine code.
    """
    import sip

    class Obj(QtCore.QObject):
        pass

    obj = Obj()
    with qtbot.waitSignal(obj.destroyed):
        obj.deleteLater()

    assert sip.isdeleted(obj)


def test_qtbot_wait(qtbot, stop_watch):
    stop_watch.start()
    qtbot.wait(100)
    stop_watch.stop()
    assert stop_watch.elapsed >= 95
