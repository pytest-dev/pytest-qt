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


def explicit_wait(qtbot, signal, timeout):
    """
    Explicit wait for the signal using blocker API.
    """
    blocker = qtbot.waitSignal(signal, timeout)
    assert blocker.signal_triggered is None
    blocker.wait()
    return blocker


def context_manager_wait(qtbot, signal, timeout):
    """
    Waiting for signal using context manager API.
    """
    with qtbot.waitSignal(signal, timeout) as blocker:
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
    ]
)
def test_signal_triggered(qtbot, wait_function, emit_delay, timeout,
                          expected_signal_triggered):
    """
    Testing for a signal in different conditions, ensuring we are obtaining
    the expected results.
    """
    signaller = Signaller()
    QtCore.QTimer.singleShot(emit_delay, signaller.signal.emit)

    # block signal until either signal is emitted or timeout is reached
    start_time = time.time()
    blocker = wait_function(qtbot, signaller.signal, timeout)

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
