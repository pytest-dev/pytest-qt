import weakref

import pytest

from pytestqt import qt_compat
from pytestqt.qt_compat import qt_api


def test_basics(qtbot):
    """
    Basic test that works more like a sanity check to ensure we are setting up a QApplication
    properly and are able to display a simple event_recorder.
    """
    assert qt_api.QApplication.instance() is not None
    widget = qt_api.QWidget()
    qtbot.addWidget(widget)
    widget.setWindowTitle("W1")
    widget.show()

    assert widget.isVisible()
    assert widget.windowTitle() == "W1"


def test_key_events(qtbot, event_recorder):
    """
    Basic key events test.
    """

    def extract(key_event):
        return (key_event.type(), key_event.key(), key_event.text())

    event_recorder.registerEvent(qt_api.QtGui.QKeyEvent, extract)

    qtbot.keyPress(event_recorder, "a")
    assert event_recorder.event_data == (
        qt_api.QEvent.KeyPress,
        int(qt_api.Qt.Key_A),
        "a",
    )

    qtbot.keyRelease(event_recorder, "a")
    assert event_recorder.event_data == (
        qt_api.QEvent.KeyRelease,
        int(qt_api.Qt.Key_A),
        "a",
    )


def test_mouse_events(qtbot, event_recorder):
    """
    Basic mouse events test.
    """

    def extract(mouse_event):
        return (mouse_event.type(), mouse_event.button(), mouse_event.modifiers())

    event_recorder.registerEvent(qt_api.QtGui.QMouseEvent, extract)

    qtbot.mousePress(event_recorder, qt_api.Qt.LeftButton)
    assert event_recorder.event_data == (
        qt_api.QEvent.MouseButtonPress,
        qt_api.Qt.LeftButton,
        qt_api.Qt.NoModifier,
    )

    qtbot.mousePress(event_recorder, qt_api.Qt.RightButton, qt_api.Qt.AltModifier)
    assert event_recorder.event_data == (
        qt_api.QEvent.MouseButtonPress,
        qt_api.Qt.RightButton,
        qt_api.Qt.AltModifier,
    )


def test_stop_for_interaction(qtbot, timer):
    """
    Test qtbot.stopForInteraction()
    """
    widget = qt_api.QWidget()
    qtbot.addWidget(widget)
    qtbot.waitForWindowShown(widget)
    timer.single_shot_callback(widget.close, 0)
    qtbot.stopForInteraction()


@pytest.mark.parametrize("show", [True, False])
@pytest.mark.parametrize("method_name", ["waitExposed", "waitActive"])
def test_wait_window(show, method_name, qtbot):
    """
    Using one of the wait-widget methods should not raise anything if the widget
    is properly displayed, otherwise should raise a TimeoutError.
    """
    method = getattr(qtbot, method_name)
    if qt_api.pytest_qt_api != "pyqt5":
        with pytest.raises(RuntimeError) as exc_info:
            with method(None, None):
                pass
        assert str(exc_info.value) == "Available in PyQt5 only"
    else:
        widget = qt_api.QWidget()
        qtbot.add_widget(widget)
        if show:
            with method(widget, timeout=1000):
                widget.show()
        else:
            with pytest.raises(qtbot.TimeoutError):
                with method(widget, timeout=100):
                    pass


@pytest.mark.parametrize("method_name", ["waitExposed", "waitActive"])
def test_wait_window_propagates_other_exception(method_name, qtbot):
    """
    Exceptions raised inside the with-statement of wait-widget methods should
    propagate properly.
    """
    if qt_api.pytest_qt_api != "pyqt5":
        pytest.skip("Available in PyQt5 only")

    method = getattr(qtbot, method_name)
    widget = qt_api.QWidget()
    qtbot.add_widget(widget)
    with pytest.raises(ValueError) as exc_info:
        with method(widget, timeout=100):
            widget.show()
            raise ValueError("some other error")
    assert str(exc_info.value) == "some other error"


def test_widget_kept_as_weakref(qtbot):
    """
    Test if the widget is kept as a weak reference in QtBot
    """
    widget = qt_api.QWidget()
    qtbot.add_widget(widget)
    widget = weakref.ref(widget)
    assert widget() is None


def test_event_processing_before_and_after_teardown(testdir):
    """
    Make sure events are processed before and after fixtures are torn down.

    The test works by creating a session object which pops() one of its events
    whenever a processEvents() occurs. Fixture and tests append values
    to the event list but expect the list to have been processed (by the pop())
    at each point of interest.

    https://github.com/pytest-dev/pytest-qt/issues/67
    """
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api
        import pytest

        @pytest.fixture(scope='session')
        def events_queue(qapp):
            class EventsQueue(qt_api.QtCore.QObject):

                def __init__(self):
                    qt_api.QtCore.QObject.__init__(self)
                    self.events = []

                def pop_later(self):
                    qapp.postEvent(self, qt_api.QEvent(qt_api.QEvent.User))

                def event(self, ev):
                    if ev.type() == qt_api.QEvent.User:
                        self.events.pop(-1)
                    return qt_api.QtCore.QObject.event(self, ev)

            return EventsQueue()

        @pytest.yield_fixture
        def fix(events_queue, qapp):
            assert events_queue.events == []
            yield
            assert events_queue.events == []
            events_queue.events.append('fixture teardown')
            events_queue.pop_later()

        @pytest.mark.parametrize('i', range(3))
        def test_events(events_queue, fix, i):
            assert events_queue.events == []
            events_queue.events.append('test event')
            events_queue.pop_later()
        """
    )
    res = testdir.runpytest()
    res.stdout.fnmatch_lines(["*3 passed in*"])


def test_header(testdir):
    testdir.makeconftest(
        """
        from pytestqt import qt_compat
        from pytestqt.qt_compat import qt_api

        def mock_get_versions():
            return qt_compat.VersionTuple('PyQtAPI', '1.0', '2.5', '3.5')

        assert hasattr(qt_api, 'get_versions')
        qt_api.get_versions = mock_get_versions
        """
    )
    res = testdir.runpytest()
    res.stdout.fnmatch_lines(
        ["*test session starts*", "PyQtAPI 1.0 -- Qt runtime 2.5 -- Qt compiled 3.5"]
    )


def test_public_api_backward_compatibility():
    """
    Test backward compatibility for version 1.6.0: since then symbols that were available from
    pytestqt.plugin have been moved to other modules to enhance navigation and maintainability,
    this test ensures the same symbols are still available from the same imports. (#90)
    """
    import pytestqt.plugin

    assert pytestqt.plugin.QtBot
    assert pytestqt.plugin.SignalBlocker
    assert pytestqt.plugin.MultiSignalBlocker
    assert pytestqt.plugin.SignalTimeoutError
    assert pytestqt.plugin.format_captured_exceptions
    assert pytestqt.plugin.capture_exceptions
    assert pytestqt.plugin.QtLoggingPlugin
    assert pytestqt.plugin.Record


def test_qvariant(tmpdir):
    """Test that make_variant and extract_from_variant work in the same way
    across all supported Qt bindings.
    """
    settings = qt_api.QtCore.QSettings(
        str(tmpdir / "foo.ini"), qt_api.QtCore.QSettings.IniFormat
    )
    settings.setValue("int", qt_api.make_variant(42))
    settings.setValue("str", qt_api.make_variant("Hello"))
    settings.setValue("empty", qt_api.make_variant())

    assert qt_api.extract_from_variant(settings.value("int")) == 42
    assert qt_api.extract_from_variant(settings.value("str")) == "Hello"
    assert qt_api.extract_from_variant(settings.value("empty")) is None


def test_widgets_closed_before_fixtures(testdir):
    """
    Ensure widgets added by "qtbot.add_widget" are closed before all other
    fixtures are teardown. (#106).
    """
    testdir.makepyfile(
        """
        import pytest
        from pytestqt.qt_compat import qt_api

        class Widget(qt_api.QWidget):

            closed = False

            def closeEvent(self, e):
                e.accept()
                self.closed = True

        @pytest.yield_fixture
        def widget(qtbot):
            w = Widget()
            qtbot.add_widget(w)
            yield w
            assert w.closed

        def test_foo(widget):
            pass
    """
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(["*= 1 passed in *"])


def test_qtbot_wait(qtbot, stop_watch):
    stop_watch.start()
    qtbot.wait(250)
    stop_watch.stop()
    assert stop_watch.elapsed >= 220


@pytest.fixture
def event_recorder(qtbot):
    class EventRecorder(qt_api.QWidget):

        """
        Widget that records some kind of events sent to it.

        When this event_recorder receives a registered event (by calling `registerEvent`), it will call
        the associated *extract* function and hold the return value from the function in the
        `event_data` member.
        """

        def __init__(self):
            qt_api.QWidget.__init__(self)
            self._event_types = {}
            self.event_data = None

        def registerEvent(self, event_type, extract_func):
            self._event_types[event_type] = extract_func

        def event(self, ev):
            for event_type, extract_func in self._event_types.items():
                if isinstance(ev, event_type):
                    self.event_data = extract_func(ev)
                    return True

            return False

    widget = EventRecorder()
    qtbot.addWidget(widget)
    return widget


@pytest.mark.parametrize(
    "value, expected",
    [
        (True, True),
        (False, False),
        ("True", True),
        ("False", False),
        ("true", True),
        ("false", False),
    ],
)
def test_parse_ini_boolean_valid(value, expected):
    import pytestqt.qtbot

    assert pytestqt.qtbot._parse_ini_boolean(value) == expected


def test_parse_ini_boolean_invalid():
    import pytestqt.qtbot

    with pytest.raises(ValueError):
        pytestqt.qtbot._parse_ini_boolean("foo")


@pytest.mark.parametrize("option_api", ["pyqt4", "pyqt5", "pyside", "pyside2"])
def test_qt_api_ini_config(testdir, monkeypatch, option_api):
    """
    Test qt_api ini option handling.
    """
    from pytestqt.qt_compat import qt_api

    monkeypatch.delenv("PYTEST_QT_API", raising=False)

    testdir.makeini(
        """
        [pytest]
        qt_api={option_api}
    """.format(
            option_api=option_api
        )
    )

    testdir.makepyfile(
        """
        import pytest

        def test_foo(qtbot):
            pass
    """
    )

    result = testdir.runpytest_subprocess()
    if qt_api.pytest_qt_api.replace("v2", "") == option_api:  # handle pyqt4v2
        result.stdout.fnmatch_lines(["* 1 passed in *"])
    else:
        try:
            ModuleNotFoundError
        except NameError:
            # Python < 3.6
            result.stderr.fnmatch_lines(["*ImportError:*"])
        else:
            # Python >= 3.6
            result.stderr.fnmatch_lines(["*ModuleNotFoundError:*"])


@pytest.mark.parametrize("envvar", ["pyqt4", "pyqt5", "pyside", "pyside2"])
def test_qt_api_ini_config_with_envvar(testdir, monkeypatch, envvar):
    """ensure environment variable wins over config value if both are present
    """
    testdir.makeini(
        """
        [pytest]
        qt_api={option_api}
    """.format(
            option_api="piecute"
        )
    )

    monkeypatch.setenv("PYTEST_QT_API", envvar)

    testdir.makepyfile(
        """
        import pytest

        def test_foo(qtbot):
            pass
    """
    )

    result = testdir.runpytest_subprocess()
    if qt_api.pytest_qt_api.replace("v2", "") == envvar:
        result.stdout.fnmatch_lines(["* 1 passed in *"])
    else:
        try:
            ModuleNotFoundError
        except NameError:
            # Python < 3.6
            result.stderr.fnmatch_lines(["*ImportError:*"])
        else:
            # Python >= 3.6
            result.stderr.fnmatch_lines(["*ModuleNotFoundError:*"])


def test_invalid_qt_api_envvar(testdir, monkeypatch):
    """
    Make sure the error message with an invalid PYQTEST_QT_API is correct.
    """
    testdir.makepyfile(
        """
        import pytest

        def test_foo(qtbot):
            pass
    """
    )
    monkeypatch.setenv("PYTEST_QT_API", "piecute")
    result = testdir.runpytest_subprocess()
    result.stderr.fnmatch_lines(["* Invalid value for $PYTEST_QT_API: piecute"])


@pytest.mark.skipif(
    qt_api.pytest_qt_api in ["pyqt4", "pyqt4v2", "pyside"],
    reason="QApplication.arguments() doesn't return custom arguments with Qt4 and Windows",
)
def test_qapp_args(testdir):
    """
    Test customizing of QApplication arguments.
    """
    testdir.makeconftest(
        """
        import pytest

        @pytest.fixture(scope='session')
        def qapp_args():
            return ['--test-arg']
        """
    )
    testdir.makepyfile(
        """
        def test_args(qapp):
            assert '--test-arg' in list(qapp.arguments())
    """
    )
    result = testdir.runpytest_subprocess()
    result.stdout.fnmatch_lines(["*= 1 passed in *"])


def test_importerror(monkeypatch):
    def _fake_import(name, *args):
        raise ImportError("Failed to import {}".format(name))

    monkeypatch.delenv("PYTEST_QT_API", raising=False)
    monkeypatch.setattr(qt_compat, "_import", _fake_import)

    expected = (
        "pytest-qt requires either PySide, PySide2, PyQt4 or PyQt5 to be installed\n"
        "  PyQt4.QtCore: Failed to import PyQt4.QtCore\n"
        "  PyQt5.QtCore: Failed to import PyQt5.QtCore\n"
        "  PySide.QtCore: Failed to import PySide.QtCore\n"
        "  PySide2.QtCore: Failed to import PySide2.QtCore"
    )

    with pytest.raises(RuntimeError, match=expected):
        qt_api.set_qt_api(api=None)
