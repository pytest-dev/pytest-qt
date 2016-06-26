import weakref
import pytest
from pytestqt.qt_compat import QtGui, Qt, QEvent, QtCore, QApplication, \
    QWidget
import pytestqt.qtbot


def test_basics(qtbot):
    """
    Basic test that works more like a sanity check to ensure we are setting up a QApplication
    properly and are able to display a simple event_recorder.
    """
    assert QApplication.instance() is not None
    widget = QWidget()
    qtbot.addWidget(widget)
    widget.setWindowTitle('W1')
    widget.show()

    assert widget.isVisible()
    assert widget.windowTitle() == 'W1'


def test_key_events(qtbot, event_recorder):
    """
    Basic key events test.
    """
    def extract(key_event):
        return (
            key_event.type(),
            key_event.key(),
            key_event.text(),
        )

    event_recorder.registerEvent(QtGui.QKeyEvent, extract)

    qtbot.keyPress(event_recorder, 'a')
    assert event_recorder.event_data == (QEvent.KeyPress, int(Qt.Key_A), 'a')

    qtbot.keyRelease(event_recorder, 'a')
    assert event_recorder.event_data == (QEvent.KeyRelease, int(Qt.Key_A), 'a')


def test_mouse_events(qtbot, event_recorder):
    """
    Basic mouse events test.
    """
    def extract(mouse_event):
        return (
            mouse_event.type(),
            mouse_event.button(),
            mouse_event.modifiers(),
        )

    event_recorder.registerEvent(QtGui.QMouseEvent, extract)

    qtbot.mousePress(event_recorder, Qt.LeftButton)
    assert event_recorder.event_data == (QEvent.MouseButtonPress, Qt.LeftButton, Qt.NoModifier)

    qtbot.mousePress(event_recorder, Qt.RightButton, Qt.AltModifier)
    assert event_recorder.event_data == (QEvent.MouseButtonPress, Qt.RightButton, Qt.AltModifier)


def test_stop_for_interaction(qtbot):
    """
    Test qtbot.stopForInteraction()
    """
    widget = QWidget()
    qtbot.addWidget(widget)
    qtbot.waitForWindowShown(widget)
    QtCore.QTimer.singleShot(0, widget.close)
    qtbot.stopForInteraction()


def test_widget_kept_as_weakref(qtbot):
    """
    Test if the widget is kept as a weak reference in QtBot
    """
    widget = QWidget()
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
        '''
        from pytestqt.qt_compat import QtCore, QEvent
        import pytest

        @pytest.fixture(scope='session')
        def events_queue(qapp):
            class EventsQueue(QtCore.QObject):

                def __init__(self):
                    QtCore.QObject.__init__(self)
                    self.events = []

                def pop_later(self):
                    qapp.postEvent(self, QEvent(QEvent.User))

                def event(self, ev):
                    if ev.type() == QEvent.User:
                        self.events.pop(-1)
                    return QtCore.QObject.event(self, ev)

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
        '''
    )
    res = testdir.runpytest()
    res.stdout.fnmatch_lines([
        '*3 passed in*',
    ])


def test_header(testdir):
    testdir.makeconftest(
        '''
        from pytestqt import qt_compat

        def mock_get_versions():
            return qt_compat.VersionTuple('PyQtAPI', '1.0', '2.5', '3.5')

        assert hasattr(qt_compat, 'get_versions')
        qt_compat.get_versions = mock_get_versions
        '''
    )
    res = testdir.runpytest()
    res.stdout.fnmatch_lines([
        '*test session starts*',
        'PyQtAPI 1.0 -- Qt runtime 2.5 -- Qt compiled 3.5',
    ])


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


def test_widgets_closed_before_fixtures(testdir):
    """
    Ensure widgets added by "qtbot.add_widget" are closed before all other
    fixtures are teardown. (#106).
    """
    testdir.makepyfile('''
        import pytest
        from pytestqt.qt_compat import QWidget

        class Widget(QWidget):

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
    ''')
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        '*= 1 passed in *'
    ])


def test_qtbot_wait(qtbot, stop_watch):
    stop_watch.start()
    qtbot.wait(250)
    stop_watch.stop()
    assert stop_watch.elapsed >= 220


class EventRecorder(QWidget):

    """
    Widget that records some kind of events sent to it.

    When this event_recorder receives a registered event (by calling `registerEvent`), it will call
    the associated *extract* function and hold the return value from the function in the
    `event_data` member.
    """

    def __init__(self):
        QWidget.__init__(self)
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


@pytest.fixture
def event_recorder(qtbot):
    widget = EventRecorder()
    qtbot.addWidget(widget)
    return widget


@pytest.mark.parametrize('value, expected', [
    (True, True),
    (False, False),
    ('True', True),
    ('False', False),
    ('true', True),
    ('false', False),
])
def test_parse_ini_boolean_valid(value, expected):
    assert pytestqt.qtbot._parse_ini_boolean(value) == expected


def test_parse_ini_boolean_invalid():
    with pytest.raises(ValueError):
        pytestqt.qtbot._parse_ini_boolean('foo')
