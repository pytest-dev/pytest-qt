import pytest
import time

from pytestqt.qt_compat import QtCore, Signal


class Signaller(QtCore.QObject):

    signal = Signal()


def test_signal_blocker_exception(qtbot):
    """
    Make sure waitSignal without signals and timeout doesn't hang, but raises
    ValueError instead.
    """
    with pytest.raises(ValueError):
        qtbot.waitSignal(None, None).wait()


def explicit_wait(qtbot, signal, timeout, raising, raises):
    """
    Explicit wait for the signal using blocker API.
    """
    blocker = qtbot.waitSignal(signal, timeout, raising=raising)
    assert not blocker.signal_triggered
    if raises:
        with pytest.raises(qtbot.SignalTimeout):
            blocker.wait()
    else:
        blocker.wait()
    return blocker


def context_manager_wait(qtbot, signal, timeout, raising, raises):
    """
    Waiting for signal using context manager API.
    """
    if raises:
        with pytest.raises(qtbot.SignalTimeout):
            with qtbot.waitSignal(signal, timeout, raising=raising) as blocker:
                pass
    else:
        with qtbot.waitSignal(signal, timeout, raising=raising) as blocker:
            pass
    return blocker


@pytest.mark.parametrize(
    ('wait_function', 'emit_delay', 'timeout', 'expected_signal_triggered',
     'raising'),
    [
        (explicit_wait, 500, 2000, True, False),
        (explicit_wait, 500, None, True, False),
        (context_manager_wait, 500, 2000, True, False),
        (context_manager_wait, 500, None, True, False),
        (explicit_wait, 2000, 500, False, False),
        (context_manager_wait, 2000, 500, False, False),

        (explicit_wait, 2000, 500, False, True),
        (context_manager_wait, 2000, 500, False, True),
        (explicit_wait, 2000, 500, False, True),
        (context_manager_wait, 2000, 500, False, True),
    ] * 2  # Running all tests twice to catch a QTimer segfault, see #42/#43.
)
def test_signal_triggered(qtbot, wait_function, emit_delay, timeout,
                          expected_signal_triggered, raising):
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
    raises = raising and not expected_signal_triggered
    blocker = wait_function(qtbot, signaller.signal, timeout, raising=raising,
                            raises=raises)

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


def test_explicit_emit(qtbot):
    """
    Make sure an explicit emit() inside a waitSignal block works.
    """
    signaller = Signaller()
    with qtbot.waitSignal(signaller.signal, timeout=5000) as waiting:
        signaller.signal.emit()

    assert waiting.signal_triggered
