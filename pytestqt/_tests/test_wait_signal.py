import pytest
import time

from pytestqt.qt_compat import QtCore, Signal


class Signaller(QtCore.QObject):

    signal = Signal()
    signal_2 = Signal()


def test_signal_blocker_exception(qtbot):
    """
    Make sure waitSignal without signals and timeout doesn't hang, but raises
    ValueError instead.
    """
    with pytest.raises(ValueError):
        qtbot.waitSignal(None, None).wait()


def explicit_wait(qtbot, signal, timeout, multiple):
    """
    Explicit wait for the signal using blocker API.
    """
    func = qtbot.waitSignals if multiple else qtbot.waitSignal
    blocker = func(signal, timeout)
    assert not blocker.signal_triggered
    blocker.wait()
    return blocker


def context_manager_wait(qtbot, signal, timeout, multiple):
    """
    Waiting for signal using context manager API.
    """
    func = qtbot.waitSignals if multiple else qtbot.waitSignal
    with func(signal, timeout) as blocker:
        pass
    return blocker


@pytest.mark.parametrize(
    ('wait_function', 'emit_delay', 'timeout', 'expected_signal_triggered'),
    [
        (explicit_wait, 500, 2000, True),
        (explicit_wait, 500, None, True),
        (context_manager_wait, 500, 2000, True),
        (context_manager_wait, 500, None, True),
        (explicit_wait, 2000, 500, False),
        (context_manager_wait, 2000, 500, False),
    ] * 2  # Running all tests twice to catch a QTimer segfault, see #42/#43.
)
def test_signal_triggered(qtbot, wait_function, emit_delay, timeout,
                          expected_signal_triggered):
    """
    Testing for a signal in different conditions, ensuring we are obtaining
    the expected results.
    """
    signaller = Signaller()

    timer = QtCore.QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(signaller.signal.emit)
    timer.start(emit_delay)

    # block signal until either signal is emitted or timeout is reached
    start_time = time.time()
    blocker = wait_function(qtbot, signaller.signal, timeout, multiple=False)

    # Check that event loop exited.
    assert not blocker._loop.isRunning()

    # ensure that either signal was triggered or timeout occurred
    assert blocker.signal_triggered == expected_signal_triggered

    # Check that we exited by the earliest parameter; timeout = None means
    # wait forever, so ensure we waited at most 4 times emit-delay
    if timeout is None:
        timeout = emit_delay * 4
    max_wait_ms = max(emit_delay, timeout)
    assert time.time() - start_time < (max_wait_ms / 1000.0)


@pytest.mark.parametrize(
    ('wait_function', 'emit_delay_1', 'emit_delay_2', 'timeout',
     'expected_signal_triggered'),
    [
        (explicit_wait, 500, 600, 2000, True),
        (explicit_wait, 500, 600, None, True),
        (context_manager_wait, 500, 600, 2000, True),
        (context_manager_wait, 500, 600, None, True),
        (explicit_wait, 2000, 2000, 500, False),
        (explicit_wait, 500, 2000, 1000, False),
        (explicit_wait, 2000, 500, 1000, False),
        (context_manager_wait, 2000, 2000, 500, False),
        (context_manager_wait, 500, 2000, 1000, False),
        (context_manager_wait, 2000, 500, 1000, False),
    ]
)
def test_signal_triggered_multiple(qtbot, wait_function, emit_delay_1,
                                   emit_delay_2, timeout,
                                   expected_signal_triggered):
    """
    Testing for a signal in different conditions, ensuring we are obtaining
    the expected results.
    """
    signaller = Signaller()

    timer = QtCore.QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(signaller.signal.emit)
    timer.start(emit_delay_1)

    timer2 = QtCore.QTimer()
    timer2.setSingleShot(True)
    timer2.timeout.connect(signaller.signal_2.emit)
    timer2.start(emit_delay_2)

    # block signal until either signal is emitted or timeout is reached
    start_time = time.time()
    blocker = wait_function(qtbot, [signaller.signal, signaller.signal_2],
                            timeout, multiple=True)

    # Check that event loop exited.
    assert not blocker._loop.isRunning()

    # ensure that either signal was triggered or timeout occurred
    assert blocker.signal_triggered == expected_signal_triggered

    # Check that we exited by the earliest parameter; timeout = None means
    # wait forever, so ensure we waited at most 4 times emit-delay
    if timeout is None:
        timeout = max(emit_delay_1, emit_delay_2) * 4
    max_wait_ms = max(emit_delay_1, emit_delay_2, timeout)
    assert time.time() - start_time < (max_wait_ms / 1000.0)


def test_explicit_emit(qtbot):
    """
    Make sure an explicit emit() inside a waitSignal block works.
    """
    signaller = Signaller()
    with qtbot.waitSignal(signaller.signal, timeout=5000) as waiting:
        signaller.signal.emit()

    assert waiting.signal_triggered


def test_explicit_emit_multiple(qtbot):
    """
    Make sure an explicit emit() inside a waitSignal block works.
    """
    signaller = Signaller()
    with qtbot.waitSignals([signaller.signal, signaller.signal_2],
                           timeout=5000) as waiting:
        signaller.signal.emit()
        signaller.signal_2.emit()

    assert waiting.signal_triggered
