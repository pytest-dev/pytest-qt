import sys

import pytest

from pytestqt.exceptions import capture_exceptions, format_captured_exceptions
from pytestqt.qt_compat import qt_api

# PySide6 is automatically captures exceptions during the event loop,
# and re-raises them when control gets back to Python, so the related
# functionality does not work, nor is needed for the end user.
exception_capture_pyside6 = pytest.mark.skipif(
    qt_api.pytest_qt_api == "pyside6",
    reason="pytest-qt capture not working/needed on PySide6",
)


@pytest.mark.parametrize("raise_error", [False, True])
def test_catch_exceptions_in_virtual_methods(testdir, raise_error):
    """
    Catch exceptions that happen inside Qt's event loop and make the
    tests fail if any.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api

        class Receiver(qt_api.QtCore.QObject):

            def event(self, ev):
                if {raise_error}:
                    try:
                        raise RuntimeError('original error')
                    except RuntimeError:
                        raise ValueError('mistakes were made')

                return qt_api.QtCore.QObject.event(self, ev)


        def test_exceptions(qtbot):
            v = Receiver()
            app = qt_api.QtWidgets.QApplication.instance()
            app.sendEvent(v, qt_api.QtCore.QEvent(qt_api.QtCore.QEvent.Type.User))
            app.sendEvent(v, qt_api.QtCore.QEvent(qt_api.QtCore.QEvent.Type.User))
            app.processEvents()

    """.format(
            raise_error=raise_error
        )
    )
    result = testdir.runpytest()
    if raise_error:
        if qt_api.pytest_qt_api == "pyside6":
            # PySide6 automatically captures exceptions during the event loop,
            # and re-raises them when control gets back to Python.
            # This results in the exception not being captured by
            # us, and a more natural traceback which includes the app.sendEvent line.
            expected_lines = [
                "*RuntimeError: original error",
                "*app.sendEvent*",
                "*ValueError: mistakes were made*",
                "*1 failed*",
            ]
        else:
            expected_lines = [
                "*Exceptions caught in Qt event loop:*",
                "RuntimeError: original error",
                "*ValueError: mistakes were made*",
                "*1 failed*",
            ]
        result.stdout.fnmatch_lines(expected_lines)
        assert "pytest.fail" not in "\n".join(result.outlines)
    else:
        result.stdout.fnmatch_lines("*1 passed*")


def test_format_captured_exceptions():
    try:
        raise ValueError("errors were made")
    except ValueError:
        exceptions = [sys.exc_info()]

    obtained_text = format_captured_exceptions(exceptions)
    lines = obtained_text.splitlines()

    assert "Exceptions caught in Qt event loop:" in lines
    assert "ValueError: errors were made" in lines


def test_format_captured_exceptions_chained():
    try:
        try:
            raise ValueError("errors were made")
        except ValueError:
            raise RuntimeError("error handling value error")
    except RuntimeError:
        exceptions = [sys.exc_info()]

    obtained_text = format_captured_exceptions(exceptions)
    lines = obtained_text.splitlines()

    assert "Exceptions caught in Qt event loop:" in lines
    assert "ValueError: errors were made" in lines
    assert "RuntimeError: error handling value error" in lines


@pytest.mark.parametrize("no_capture_by_marker", [True, False])
@exception_capture_pyside6
def test_no_capture(testdir, no_capture_by_marker):
    """
    Make sure options that disable exception capture are working (either marker
    or ini configuration value).

    :type testdir: TmpTestdir
    """
    if no_capture_by_marker:
        marker_code = "@pytest.mark.qt_no_exception_capture"
    else:
        marker_code = ""
        testdir.makeini(
            """
            [pytest]
            qt_no_exception_capture = 1
            """
        )
    testdir.makepyfile(
        f"""
        import pytest
        import sys
        from pytestqt.qt_compat import qt_api

        # PyQt 5.5+ will crash if there's no custom exception handler installed.
        sys.excepthook = lambda *args: None

        class MyWidget(qt_api.QtWidgets.QWidget):

            def mouseReleaseEvent(self, ev):
                raise RuntimeError

        {marker_code}
        def test_widget(qtbot):
            w = MyWidget()
            qtbot.addWidget(w)
            qtbot.mouseClick(w, qt_api.QtCore.Qt.MouseButton.LeftButton)
        """
    )
    res = testdir.runpytest()
    res.stdout.fnmatch_lines(["*1 passed*"])


def test_no_capture_preserves_custom_excepthook(testdir):
    """
    Capturing must leave custom excepthooks alone when disabled.

    :type testdir: TmpTestdir
    """
    testdir.makepyfile(
        """
        import pytest
        import sys
        from pytestqt.qt_compat import qt_api

        def custom_excepthook(*args):
            sys.__excepthook__(*args)

        sys.excepthook = custom_excepthook

        @pytest.mark.qt_no_exception_capture
        def test_no_capture(qtbot):
            assert sys.excepthook is custom_excepthook

        def test_capture(qtbot):
            assert sys.excepthook is not custom_excepthook
    """
    )
    res = testdir.runpytest()
    res.stdout.fnmatch_lines(["*2 passed*"])


def test_exception_capture_on_call(testdir):
    """
    Exceptions should also be captured during test execution.

    :type testdir: TmpTestdir
    """
    testdir.makepyfile(
        """
        import pytest
        from pytestqt.qt_compat import qt_api

        class MyWidget(qt_api.QtWidgets.QWidget):

            def event(self, ev):
                raise RuntimeError('event processed')

        def test_widget(qtbot, qapp):
            w = MyWidget()
            qapp.postEvent(w, qt_api.QtCore.QEvent(QEvent.Type.User))
            qapp.processEvents()
    """
    )
    res = testdir.runpytest("-s")
    res.stdout.fnmatch_lines(["*RuntimeError('event processed')*", "*1 failed*"])


def test_exception_capture_on_widget_close(testdir):
    """
    Exceptions should also be captured when widget is being closed.

    :type testdir: TmpTestdir
    """
    testdir.makepyfile(
        """
        import pytest
        from pytestqt.qt_compat import qt_api

        class MyWidget(qt_api.QtWidgets.QWidget):

            def closeEvent(self, ev):
                raise RuntimeError('close error')

        def test_widget(qtbot, qapp):
            w = MyWidget()
            test_widget.w = w  # keep it alive
            qtbot.addWidget(w)
    """
    )
    res = testdir.runpytest("-s")
    res.stdout.fnmatch_lines(["*RuntimeError('close error')*", "*1 error*"])


@pytest.mark.parametrize("mode", ["setup", "teardown"])
def test_exception_capture_on_fixture_setup_and_teardown(testdir, mode):
    """
    Setup/teardown exception capturing as early/late as possible to catch
    all exceptions, even from other fixtures (#105).

    :type testdir: TmpTestdir
    """
    if mode == "setup":
        setup_code = "send_event(w, qapp)"
        teardown_code = ""
    else:
        setup_code = ""
        teardown_code = "send_event(w, qapp)"

    testdir.makepyfile(
        """
        import pytest
        from pytestqt.qt_compat import qt_api

        class MyWidget(qt_api.QtWidgets.QWidget):

            def event(self, ev):
                if ev.type() == qt_api.QtCore.QEvent.Type.User:
                    raise RuntimeError('event processed')
                return True

        @pytest.fixture
        def widget(qapp):
            w = MyWidget()
            {setup_code}
            yield w
            {teardown_code}

        def send_event(w, qapp):
            qapp.postEvent(w, qt_api.QtCore.QEvent(
                qt_api.QtCore.QEvent.Type.User))
            qapp.processEvents()

        def test_capture(widget):
            pass
    """.format(
            setup_code=setup_code, teardown_code=teardown_code
        )
    )
    res = testdir.runpytest("-s")
    res.stdout.fnmatch_lines(
        [
            "*__ ERROR at %s of test_capture __*" % mode,
            "*RuntimeError('event processed')*",
            "*1 error*",
        ]
    )


@pytest.mark.qt_no_exception_capture
@exception_capture_pyside6
def test_capture_exceptions_context_manager(qapp):
    """Test capture_exceptions() context manager.

    While not used internally anymore, it is still part of the API and therefore
    should be properly tested.
    """
    from pytestqt.qt_compat import qt_api
    from pytestqt.exceptions import capture_exceptions

    class Receiver(qt_api.QtCore.QObject):
        def event(self, ev):
            raise ValueError("mistakes were made")

    r = Receiver()
    with capture_exceptions() as exceptions:
        qapp.sendEvent(r, qt_api.QtCore.QEvent(qt_api.QtCore.QEvent.Type.User))
        qapp.processEvents()

    assert [str(e) for (t, e, tb) in exceptions] == ["mistakes were made"]


def test_capture_exceptions_qtbot_context_manager(testdir):
    """Test capturing exceptions in a block by using `capture_exceptions` method provided
    by `qtbot`.
    """
    testdir.makepyfile(
        """
        import pytest
        from pytestqt.qt_compat import qt_api

        class MyWidget(qt_api.QtWidgets.QWidget):

            on_event = qt_api.Signal()

        def test_widget(qtbot):
            widget = MyWidget()
            qtbot.addWidget(widget)

            def raise_on_event():
                raise RuntimeError("error")

            widget.on_event.connect(raise_on_event)

            with qtbot.capture_exceptions() as exceptions:
                widget.on_event.emit()

            assert len(exceptions) == 1
            assert str(exceptions[0][1]) == "error"
    """
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(["*1 passed*"])


@exception_capture_pyside6
def test_exceptions_to_stderr(qapp, capsys):
    """
    Exceptions should still be reported to stderr.
    """
    called = []
    from pytestqt.qt_compat import qt_api

    class MyWidget(qt_api.QtWidgets.QWidget):
        def event(self, ev):
            called.append(1)
            raise RuntimeError("event processed")

    w = MyWidget()
    with capture_exceptions() as exceptions:
        qapp.postEvent(w, qt_api.QtCore.QEvent(qt_api.QtCore.QEvent.Type.User))
        qapp.processEvents()
    assert called
    del exceptions[:]
    _out, err = capsys.readouterr()
    assert 'raise RuntimeError("event processed")' in err


@exception_capture_pyside6
def test_exceptions_dont_leak(testdir):
    """
    Ensure exceptions are cleared when an exception occurs and don't leak (#187).
    """
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api
        import gc
        import weakref

        class MyWidget(qt_api.QtWidgets.QWidget):

            def event(self, ev):
                called.append(1)
                raise RuntimeError('event processed')

        weak_ref = None
        called = []

        def test_1(qapp):
            global weak_ref
            w = MyWidget()
            weak_ref = weakref.ref(w)
            qapp.postEvent(w, qt_api.QtCore.QEvent(qt_api.QtCore.QEvent.Type.User))
            qapp.processEvents()

        def test_2(qapp):
            assert called
            gc.collect()
            assert weak_ref() is None
    """
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(["*1 failed, 1 passed*"])
