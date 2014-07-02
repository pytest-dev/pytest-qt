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
    start_time = time.time()
    blocker.wait()
    return blocker._loop, start_time


def context_manager_wait(qtbot, signal, timeout):
    """
    Waiting for signal using context manager API.
    """
    with qtbot.waitSignal(signal, timeout) as blocker:
        start_time = time.time()
    return blocker._loop, start_time


@pytest.mark.parametrize(
    ('wait_function', 'emit_delay', 'timeout'),
    [
        (explicit_wait, 500, 2000),
        (explicit_wait, 500, None),
        (context_manager_wait, 500, 2000),
        (context_manager_wait, 500, None),
    ]
)
def test_signal_triggered(qtbot, wait_function, emit_delay, timeout):
    """
    Ensure that a signal being triggered before timeout expires makes the
    loop quitting early.
    """
    signaller = Signaller()
    QtCore.QTimer.singleShot(emit_delay, signaller.signal.emit)

    # block signal until either signal is emitted or timeout is reached
    loop, start_time = wait_function(qtbot, signaller.signal, timeout)

    # Check that event loop exited.
    assert not loop.isRunning()

    # Check that we exited by the earliest parameter; timeout = None means
    # wait forever, so ensure we waited at most 4 times emit-delay
    if timeout is None:
        timeout = emit_delay * 4
    max_wait_ms = max(emit_delay, timeout)
    assert time.time() - start_time < (max_wait_ms / 1000.0)
