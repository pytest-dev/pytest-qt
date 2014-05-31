import pytest
from pytestqt.qt_compat import QtGui, Qt, QtCore


class Receiver(QtCore.QObject):

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


