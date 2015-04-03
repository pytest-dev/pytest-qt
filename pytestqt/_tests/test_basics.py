import weakref
import pytest
from pytestqt.qt_compat import QtGui, Qt, QEvent, QtCore, QApplication, \
    QWidget


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
