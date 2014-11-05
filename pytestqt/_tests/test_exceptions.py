import pytest
import sys
from pytestqt.plugin import capture_exceptions, format_captured_exceptions
from pytestqt.qt_compat import QtGui, Qt, QtCore


pytest_plugins = 'pytester'


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


@pytest.mark.parametrize('no_capture_by_marker', [True, False])
def test_no_capture(testdir, no_capture_by_marker):
    """
    Make sure options that disable exception capture are working (either marker
    or ini configuration value).
    :type testdir: TmpTestdir
    """
    if no_capture_by_marker:
        marker_code = '@pytest.mark.qt_no_exception_capture'
    else:
        marker_code = ''
        testdir.makeini('''
            [pytest]
            qt_no_exception_capture = 1
        ''')
    testdir.makepyfile('''
        import pytest
        from pytestqt.qt_compat import QtGui, QtCore

        class MyWidget(QtGui.QWidget):

            def mouseReleaseEvent(self, ev):
                raise RuntimeError

        {marker_code}
        def test_widget(qtbot):
            w = MyWidget()
            qtbot.addWidget(w)
            qtbot.mouseClick(w, QtCore.Qt.LeftButton)
    '''.format(marker_code=marker_code))
    result = testdir.runpytest('-s')
    # when it fails, it fails with "1 passed, 1 error in", so ensure
    # it is passing without errors
    result.stdout.fnmatch_lines('*1 passed in*')