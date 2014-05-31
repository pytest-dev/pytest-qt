import textwrap
import pytest
import sys
from pytestqt.plugin import capture_exceptions, format_captured_exceptions
from pytestqt.qt_compat import QtGui, Qt, QtCore


class Receiver(QtCore.QObject):
    """
    Dummy QObject subclass that raises an error on receiving events if
    `raise_error` is True.
    """

    def __init__(self, raise_error, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self._raise_error = raise_error


    def event(self, ev):
        if self._raise_error:
            raise ValueError('mistakes were made')
        return QtCore.QObject.event(self, ev)


@pytest.mark.parametrize('raise_error', [False, pytest.mark.xfail(True)])
def test_catch_exceptions_in_virtual_methods(qtbot, raise_error):
    """
    Catch exceptions that happen inside Qt virtual methods and make the
    tests fail if any.
    """
    v = Receiver(raise_error)
    app = QtGui.QApplication.instance()
    app.sendEvent(v, QtCore.QEvent(QtCore.QEvent.User))
    app.sendEvent(v, QtCore.QEvent(QtCore.QEvent.User))
    app.processEvents()


def test_format_captured_exceptions():
    try:
        raise ValueError('errors were made')
    except ValueError:
        exceptions = [sys.exc_info()]

    obtained_text = format_captured_exceptions(exceptions)
    lines = obtained_text.splitlines()

    assert 'Qt exceptions in virtual methods:' in lines
    assert 'ValueError: errors were made' in lines