import pytest
import sys
from pytestqt.plugin import format_captured_exceptions, QT_API


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
        assert 'pytest.fail' not in '\n'.join(result.outlines)
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
        import sys
        from pytestqt.qt_compat import QWidget, QtCore

        # PyQt 5.5+ will crash if there's no custom exception handler installed
        sys.excepthook = lambda *args: None

        class MyWidget(QWidget):

            def mouseReleaseEvent(self, ev):
                raise RuntimeError

        {marker_code}
        def test_widget(qtbot):
            w = MyWidget()
            qtbot.addWidget(w)
            qtbot.mouseClick(w, QtCore.Qt.LeftButton)
    '''.format(marker_code=marker_code))
    res = testdir.runpytest()
    res.stdout.fnmatch_lines(['*1 passed*'])


def test_exception_capture_on_teardown(testdir):
    """
    Exceptions should also be captured during test teardown.

    :type testdir: TmpTestdir
    """
    testdir.makepyfile('''
        import pytest
        from pytestqt.qt_compat import QWidget, QtCore, QEvent

        class MyWidget(QWidget):

            def event(self, ev):
                raise RuntimeError('event processed')

        def test_widget(qtbot, qapp):
            w = MyWidget()
            # keep a reference to the widget so it will lives after the test
            # ends. This will in turn trigger its event() during test tear down,
            # raising the exception during its event processing
            test_widget.w = w
            qapp.postEvent(w, QEvent(QEvent.User))
    ''')
    res = testdir.runpytest('-s')
    res.stdout.fnmatch_lines([
        "*RuntimeError('event processed')*",
        '*1 error*',
    ])

