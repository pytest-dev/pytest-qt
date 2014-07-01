import pytest
import time

from pytestqt.qt_compat import QtCore, Signal


def test_signal_blocker_exception(qtbot):
    with pytest.raises(ValueError):
        qtbot.waitSignal(None, None).wait()


class Signaller(QtCore.QObject):

    signal = Signal()


def test_wait_signal_context_manager(qtbot, monkeypatch):
    signaller = Signaller()

    # Emit a signal after half a second, and block the signal with a timeout
    # of 2 seconds.
    QtCore.QTimer.singleShot(500, signaller.signal.emit)
    with qtbot.waitSignal(signaller.signal, 2000) as blocker:
        saved_loop = blocker.loop
        start_time = time.time()

    # Check that event loop exited.
    assert not saved_loop.isRunning()
    # Check that it didn't exit by a timeout.
    assert time.time() - start_time < 2  # Less than 2 seconds elapsed


def test_wait_signal_function(qtbot, monkeypatch):
    signaller = Signaller()

    # Emit a signal after half a second, and block the signal with a timeout
    # of 2 seconds.
    QtCore.QTimer.singleShot(500, signaller.signal.emit)
    blocker = qtbot.waitSignal(signaller.signal, 2000)
    start_time = time.time()
    blocker.wait()

    # Check that event loop exited.
    assert not blocker.loop.isRunning()
    # Check that it didn't exit by a timeout.
    assert time.time() - start_time < 2  # Less than 2 seconds elapsed
