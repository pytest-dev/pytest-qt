import pytest
import sys
from pytestqt.plugin import format_captured_exceptions


pytest_plugins = 'pytester'


@pytest.mark.parametrize('raise_error', [False, True])
def test_catch_exceptions_in_virtual_methods(testdir, raise_error):
    """
    Catch exceptions that happen inside Qt virtual methods and make the
    tests fail if any.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makepyfile('''
        from pytestqt.qt_compat import QtCore, QApplication

        class Receiver(QtCore.QObject):

            def event(self, ev):
                if {raise_error}:
                    raise ValueError('mistakes were made')
                return QtCore.QObject.event(self, ev)


        def test_exceptions(qtbot):
            v = Receiver()
            app = QApplication.instance()
            app.sendEvent(v, QtCore.QEvent(QtCore.QEvent.User))
            app.sendEvent(v, QtCore.QEvent(QtCore.QEvent.User))
            app.processEvents()

    '''.format(raise_error=raise_error))
    result = testdir.runpytest()
    if raise_error:
        result.stdout.fnmatch_lines([
            '*Qt exceptions in virtual methods:*',
            '*ValueError: mistakes were made*',
            '*1 error*',
        ])
    else:
        result.stdout.fnmatch_lines('*1 passed*')


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
        from pytestqt.qt_compat import QWidget, QtCore

        class MyWidget(QWidget):

            def mouseReleaseEvent(self, ev):
                raise RuntimeError

        {marker_code}
        def test_widget(qtbot):
            w = MyWidget()
            qtbot.addWidget(w)
            qtbot.mouseClick(w, QtCore.Qt.LeftButton)
    '''.format(marker_code=marker_code))
    res = testdir.inline_run()
    res.assertoutcome(passed=1)
