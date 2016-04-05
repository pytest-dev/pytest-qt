import pytest
import sys
from pytestqt.exceptions import format_captured_exceptions, capture_exceptions


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
            '*1 failed*',
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


def test_no_capture_preserves_custom_excepthook(testdir):
    """
    Capturing must leave custom excepthooks alone when disabled.

    :type testdir: TmpTestdir
    """
    testdir.makepyfile('''
        import pytest
        import sys
        from pytestqt.qt_compat import QWidget, QtCore

        def custom_excepthook(*args):
            sys.__excepthook__(*args)

        sys.excepthook = custom_excepthook

        @pytest.mark.qt_no_exception_capture
        def test_no_capture(qtbot):
            assert sys.excepthook is custom_excepthook

        def test_capture(qtbot):
            assert sys.excepthook is not custom_excepthook
    ''')
    res = testdir.runpytest()
    res.stdout.fnmatch_lines(['*2 passed*'])


def test_exception_capture_on_call(testdir):
    """
    Exceptions should also be captured during test execution.

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
            qapp.postEvent(w, QEvent(QEvent.User))
            qapp.processEvents()
    ''')
    res = testdir.runpytest('-s')
    res.stdout.fnmatch_lines([
        "*RuntimeError('event processed')*",
        '*1 failed*',
    ])


def test_exception_capture_on_widget_close(testdir):
    """
    Exceptions should also be captured when widget is being closed.

    :type testdir: TmpTestdir
    """
    testdir.makepyfile('''
        import pytest
        from pytestqt.qt_compat import QWidget, QtCore, QEvent

        class MyWidget(QWidget):

            def closeEvent(self, ev):
                raise RuntimeError('close error')

        def test_widget(qtbot, qapp):
            w = MyWidget()
            test_widget.w = w  # keep it alive
            qtbot.addWidget(w)
    ''')
    res = testdir.runpytest('-s')
    res.stdout.fnmatch_lines([
        "*RuntimeError('close error')*",
        '*1 error*',
    ])


@pytest.mark.parametrize('mode', ['setup', 'teardown'])
def test_exception_capture_on_fixture_setup_and_teardown(testdir, mode):
    """
    Setup/teardown exception capturing as early/late as possible to catch
    all exceptions, even from other fixtures (#105).

    :type testdir: TmpTestdir
    """
    if mode == 'setup':
        setup_code = 'send_event(w, qapp)'
        teardown_code = ''
    else:
        setup_code = ''
        teardown_code = 'send_event(w, qapp)'

    testdir.makepyfile('''
        import pytest
        from pytestqt.qt_compat import QWidget, QtCore, QEvent, QApplication

        class MyWidget(QWidget):

            def event(self, ev):
                if ev.type() == QEvent.User:
                    raise RuntimeError('event processed')
                return True

        @pytest.yield_fixture
        def widget(qapp):
            w = MyWidget()
            {setup_code}
            yield w
            {teardown_code}

        def send_event(w, qapp):
            qapp.postEvent(w, QEvent(QEvent.User))
            qapp.processEvents()

        def test_capture(widget):
            pass
    '''.format(setup_code=setup_code, teardown_code=teardown_code))
    res = testdir.runpytest('-s')
    res.stdout.fnmatch_lines([
        '*__ ERROR at %s of test_capture __*' % mode,
        "*RuntimeError('event processed')*",
        '*1 error*',
    ])


@pytest.mark.qt_no_exception_capture
def test_capture_exceptions_context_manager(qapp):
    """Test capture_exceptions() context manager.

    While not used internally anymore, it is still part of the API and therefore
    should be properly tested.
    """
    from pytestqt.qt_compat import QtCore
    from pytestqt.plugin import capture_exceptions

    class Receiver(QtCore.QObject):

        def event(self, ev):
            raise ValueError('mistakes were made')

    r = Receiver()
    with capture_exceptions() as exceptions:
        qapp.sendEvent(r, QtCore.QEvent(QtCore.QEvent.User))
        qapp.processEvents()

    assert [str(e) for (t, e, tb) in exceptions] == ['mistakes were made']


def test_exceptions_to_stderr(qapp):
    """
    Exceptions should still be reported to stderr.
    """
    try:
        from io import StringIO
    except:
        from StringIO import StringIO
    old = sys.stderr
    new = sys.stderr = StringIO()
    
    try:
        called = []
        from pytestqt.qt_compat import QWidget, QEvent

        class MyWidget(QWidget):

            def event(self, ev):
                called.append(1)
                raise RuntimeError('event processed')

        w = MyWidget()
        with capture_exceptions() as exceptions:
            qapp.postEvent(w, QEvent(QEvent.User))
            qapp.processEvents()
            assert called
            del exceptions[:]
            assert "raise RuntimeError('event processed')" in new.getvalue()
    finally:
        sys.stderr = old
