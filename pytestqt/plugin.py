import collections
from contextlib import contextmanager
import functools
import sys
import traceback
import weakref
import datetime

import pytest

from pytestqt.qt_compat import QtCore, QtTest, QApplication, QT_API, \
    qInstallMsgHandler, QtDebugMsg, QtWarningMsg, QtCriticalMsg, QtFatalMsg


def _inject_qtest_methods(cls):
    """
    Injects QTest methods into the given class QtBot, so the user can access
    them directly without having to import QTest.
    """

    def create_qtest_proxy_method(method_name):

        if hasattr(QtTest.QTest, method_name):
            qtest_method = getattr(QtTest.QTest, method_name)

            def result(*args, **kwargs):
                return qtest_method(*args, **kwargs)

            functools.update_wrapper(result, qtest_method)
            return staticmethod(result)
        else:
            return None  # pragma: no cover

    # inject methods from QTest into QtBot
    method_names = [
        'keyPress',
        'keyClick',
        'keyClicks',
        'keyEvent',
        'keyPress',
        'keyRelease',
        'keyToAscii',

        'mouseClick',
        'mouseDClick',
        'mouseEvent',
        'mouseMove',
        'mousePress',
        'mouseRelease',
    ]
    for method_name in method_names:
        method = create_qtest_proxy_method(method_name)
        if method is not None:
            setattr(cls, method_name, method)

    return cls


@_inject_qtest_methods
class QtBot(object):

    """
    Instances of this class are responsible for sending events to `Qt` objects (usually widgets),
    simulating user input.

    .. important:: Instances of this class should be accessed only by using a ``qtbot`` fixture,
                    never instantiated directly.

    **Widgets**

    .. automethod:: addWidget
    .. automethod:: waitForWindowShown
    .. automethod:: stopForInteraction

    **Signals**

    .. automethod:: waitSignal

    **Raw QTest API**

    Methods below provide very low level functions, as sending a single mouse click or a key event.
    Those methods are just forwarded directly to the `QTest API`_. Consult the documentation for more
    information.

    ---

    Below are methods used to simulate sending key events to widgets:

    .. staticmethod:: keyPress(widget, key[, modifier=Qt.NoModifier[, delay=-1]])
    .. staticmethod:: keyClick (widget, key[, modifier=Qt.NoModifier[, delay=-1]])
    .. staticmethod:: keyClicks (widget, key sequence[, modifier=Qt.NoModifier[, delay=-1]])
    .. staticmethod:: keyEvent (action, widget, key[, modifier=Qt.NoModifier[, delay=-1]])
    .. staticmethod:: keyPress (widget, key[, modifier=Qt.NoModifier[, delay=-1]])
    .. staticmethod:: keyRelease (widget, key[, modifier=Qt.NoModifier[, delay=-1]])

        Sends one or more keyword events to a widget.

        :param QWidget widget: the widget that will receive the event

        :param str|int key: key to send, it can be either a Qt.Key_* constant or a single character string.

        .. _keyboard modifiers:

        :param Qt.KeyboardModifier modifier: flags OR'ed together representing other modifier keys
            also pressed. Possible flags are:

            * ``Qt.NoModifier``: No modifier key is pressed.
            * ``Qt.ShiftModifier``: A Shift key on the keyboard is pressed.
            * ``Qt.ControlModifier``: A Ctrl key on the keyboard is pressed.
            * ``Qt.AltModifier``: An Alt key on the keyboard is pressed.
            * ``Qt.MetaModifier``: A Meta key on the keyboard is pressed.
            * ``Qt.KeypadModifier``: A keypad button is pressed.
            * ``Qt.GroupSwitchModifier``: X11 only. A Mode_switch key on the keyboard is pressed.

        :param int delay: after the event, delay the test for this miliseconds (if > 0).


    .. staticmethod:: keyToAscii (key)

        Auxilliary method that converts the given constant ot its equivalent ascii.

        :param Qt.Key_* key: one of the constants for keys in the Qt namespace.

        :return type: str
        :returns: the equivalent character string.

        .. note:: this method is not available in PyQt.

    ---

    Below are methods used to simulate sending mouse events to widgets.

    .. staticmethod:: mouseClick (widget, button[, stateKey=0[, pos=QPoint()[, delay=-1]]])
    .. staticmethod:: mouseDClick (widget, button[, stateKey=0[, pos=QPoint()[, delay=-1]]])
    .. staticmethod:: mouseEvent (action, widget, button, stateKey, pos[, delay=-1])
    .. staticmethod:: mouseMove (widget[, pos=QPoint()[, delay=-1]])
    .. staticmethod:: mousePress (widget, button[, stateKey=0[, pos=QPoint()[, delay=-1]]])
    .. staticmethod:: mouseRelease (widget, button[, stateKey=0[, pos=QPoint()[, delay=-1]]])

        Sends a mouse moves and clicks to a widget.

        :param QWidget widget: the widget that will receive the event

        :param Qt.MouseButton button: flags OR'ed together representing the button pressed.
            Possible flags are:

            * ``Qt.NoButton``: The button state does not refer to any button (see QMouseEvent.button()).
            * ``Qt.LeftButton``: The left button is pressed, or an event refers to the left button. (The left button may be the right button on left-handed mice.)
            * ``Qt.RightButton``: The right button.
            * ``Qt.MidButton``: The middle button.
            * ``Qt.MiddleButton``: The middle button.
            * ``Qt.XButton1``: The first X button.
            * ``Qt.XButton2``: The second X button.

        :param Qt.KeyboardModifier modifier: flags OR'ed together representing other modifier keys
            also pressed. See `keyboard modifiers`_.

        :param QPoint position: position of the mouse pointer.

        :param int delay: after the event, delay the test for this miliseconds (if > 0).


    .. _QTest API: http://doc.qt.digia.com/4.8/qtest.html

    """

    def __init__(self, app):
        """
        :param QApplication app:
            The current QApplication instance.
        """
        self._app = app
        self._widgets = []  # list of weakref to QWidget instances

    def _close(self):
        """
        Clear up method. Called at the end of each test that uses a ``qtbot`` fixture.
        """
        for w in self._widgets:
            w = w()
            if w is not None:
                w.close()
        self._widgets[:] = []

    def addWidget(self, widget):
        """
        Adds a widget to be tracked by this bot. This is not required, but will ensure that the
        widget gets closed by the end of the test, so it is highly recommended.

        :param QWidget widget:
            Widget to keep track of.
        """
        self._widgets.append(weakref.ref(widget))

    add_widget = addWidget  # pep-8 alias

    def waitForWindowShown(self, widget):
        """
        Waits until the window is shown in the screen. This is mainly useful for asynchronous
        systems like X11, where a window will be mapped to screen some time after being asked to
        show itself on the screen.

        :param QWidget widget:
            Widget to wait on.

        .. note:: In Qt5, the actual method called is qWaitForWindowExposed,
            but this name is kept for backward compatibility
        """
        if hasattr(QtTest.QTest, 'qWaitForWindowShown'): # pragma: no cover
            # PyQt4 and PySide
            QtTest.QTest.qWaitForWindowShown(widget)
        else: # pragma: no cover
            # PyQt5
            QtTest.QTest.qWaitForWindowExposed(widget)

    wait_for_window_shown = waitForWindowShown  # pep-8 alias

    def stopForInteraction(self):
        """
        Stops the current test flow, letting the user interact with any visible widget.

        This is mainly useful so that you can verify the current state of the program while writing
        tests.

        Closing the windows should resume the test run, with ``qtbot`` attempting to restore visibility
        of the widgets as they were before this call.

        .. note:: As a convenience, it is also aliased as `stop`.
        """
        widget_and_visibility = []
        for weak_widget in self._widgets:
            widget = weak_widget()
            if widget is not None:
                widget_and_visibility.append((widget, widget.isVisible()))

        self._app.exec_()

        for widget, visible in widget_and_visibility:
            widget.setVisible(visible)

    stop = stopForInteraction

    def waitSignal(self, signal=None, timeout=1000):
        """
        Stops current test until a signal is triggered.

        Used to stop the control flow of a test until a signal is emitted, or
        a number of milliseconds, specified by ``timeout``, has elapsed.

        Best used as a context manager::

           with qtbot.waitSignal(signal, timeout=1000):
               long_function_that_calls_signal()

        Also, you can use the :class:`SignalBlocker` directly if the context
        manager form is not convenient::

           blocker = qtbot.waitSignal(signal, timeout=1000)
           blocker.connect(other_signal)
           long_function_that_calls_signal()
           blocker.wait()

        :param Signal signal:
            A signal to wait for. Set to ``None`` to just use timeout.
        :param int timeout:
            How many milliseconds to wait before resuming control flow.
        :returns:
            ``SignalBlocker`` object. Call ``SignalBlocker.wait()`` to wait.

        .. note::
           Cannot have both ``signals`` and ``timeout`` equal ``None``, or
           else you will block indefinitely. We throw an error if this occurs.

        """
        blocker = SignalBlocker(timeout=timeout)
        if signal is not None:
            blocker.connect(signal)
        return blocker

    wait_signal = waitSignal  # pep-8 alias


class SignalBlocker(object):

    """
    Returned by :meth:`QtBot.waitSignal` method.

    .. automethod:: wait
    .. automethod:: connect

    :ivar int timeout: maximum time to wait for a signal to be triggered. Can
        be changed before :meth:`wait` is called.

    :ivar bool signal_triggered: set to ``True`` if a signal was triggered, or
        ``False`` if timeout was reached instead. Until :meth:`wait` is called,
        this is set to ``None``.
    """

    def __init__(self, timeout=1000):
        self._loop = QtCore.QEventLoop()
        self._signals = []
        self.timeout = timeout
        self.signal_triggered = False

    def wait(self):
        """
        Waits until either a connected signal is triggered or timeout is reached.

        :raise ValueError: if no signals are connected and timeout is None; in
            this case it would wait forever.
        """
        if self.signal_triggered:
            return
        if self.timeout is None and len(self._signals) == 0:
            raise ValueError("No signals or timeout specified.")
        if self.timeout is not None:
            QtCore.QTimer.singleShot(self.timeout, self._loop.quit)
        self._loop.exec_()

    def connect(self, signal):
        """
        Connects to the given signal, making :meth:`wait()` return once this signal
        is emitted.

        :param signal: QtCore.Signal
        """
        signal.connect(self._quit_loop_by_signal)
        self._signals.append(signal)

    def _quit_loop_by_signal(self):
        """
        quits the event loop and marks that we finished because of a signal.
        """
        self.signal_triggered = True
        self._loop.quit()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.wait()


@contextmanager
def capture_exceptions():
    """
    Context manager that captures exceptions that happen insides its context,
    and returns them as a list of (type, value, traceback) after the
    context ends.
    """
    result = []

    def hook(type_, value, tback):
        result.append((type_, value, tback))
        sys.__excepthook__(type_, value, tback)

    sys.excepthook = hook
    try:
        yield result
    finally:
        sys.excepthook = sys.__excepthook__


def format_captured_exceptions(exceptions):
    """
    Formats exceptions given as (type, value, traceback) into a string
    suitable to display as a test failure.
    """
    message = 'Qt exceptions in virtual methods:\n'
    message += '_' * 80 + '\n'
    for (exc_type, value, tback) in exceptions:
        message += ''.join(traceback.format_tb(tback)) + '\n'
        message += '%s: %s\n' % (exc_type.__name__, value)
        message += '_' * 80 + '\n'
    return message


@pytest.yield_fixture(scope='session')
def qapp():
    """
    fixture that instantiates the QApplication instance that will be used by
    the tests.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        yield app
        app.exit()
        app.deleteLater()
    else:
        yield app  # pragma: no cover


@pytest.yield_fixture
def qtbot(qapp, request):
    """
    Fixture used to create a QtBot instance for using during testing.

    Make sure to call addWidget for each top-level widget you create to ensure
    that they are properly closed after the test ends.
    """
    result = QtBot(qapp)
    no_capture = request.node.get_marker('qt_no_exception_capture') or \
                 request.config.getini('qt_no_exception_capture')
    if no_capture:
        yield result  # pragma: no cover
    else:
        with capture_exceptions() as exceptions:
            yield result
        if exceptions:
            pytest.fail(format_captured_exceptions(exceptions))

    result._close()


def pytest_addoption(parser):
    parser.addini('qt_no_exception_capture',
                  'disable automatic exception capture')

    parser.addoption('--no-qt-log', dest='qt_log', action='store_false',
                     default=True)
    parser.addoption('--qt-log-format', dest='qt_log_format',
                     default='{rec.type_name}: {rec.message}')


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        "qt_no_exception_capture: Disables pytest-qt's automatic exception "
        'capture for just one test item.')

    if config.getoption('qt_log'):
        config.pluginmanager.register(QtLoggingPlugin(config), '_qt_logging')


def pytest_report_header():
    return ['qt-api: %s' % QT_API]


@pytest.fixture
def qtlog(request):
    """Fixture that can access messages captured during testing"""
    if hasattr(request._pyfuncitem, 'qt_log_capture'):
        return request._pyfuncitem.qt_log_capture
    else:
        return _QtMessageCapture()  # pragma: no cover


class QtLoggingPlugin(object):
    """
    Pluging responsible for installing a QtMessageHandler before each
    test and augment reporting if the test failed with the messages captured.
    """

    def __init__(self, config):
        self.config = config

    def pytest_runtest_setup(self, item):
        item.qt_log_capture = _QtMessageCapture()
        previous_handler = qInstallMsgHandler(item.qt_log_capture._handle)
        item.qt_previous_handler = previous_handler

    @pytest.mark.hookwrapper
    def pytest_runtest_makereport(self, item, call):
        """Add captured Qt messages to test item report if the call failed."""

        outcome = yield
        report = outcome.result

        if call.when == 'call':

            if not report.passed:
                long_repr = getattr(report, 'longrepr', None)
                if hasattr(long_repr, 'addsection'):  # pragma: no cover
                    lines = []
                    for rec in item.qt_log_capture.records:
                        log_format = self.config.getoption('qt_log_format')
                        lines.append(log_format.format(rec=rec))
                    if lines:
                        long_repr.addsection('Captured Qt messages',
                                             '\n'.join(lines))

            qInstallMsgHandler(item.qt_previous_handler)
            del item.qt_previous_handler
            del item.qt_log_capture


class _QtMessageCapture(object):
    """
    Captures Qt messages when its `handle` method is installed using
    qInstallMsgHandler, and stores them into `messages` attribute.

    :attr messages: list of Record named-tuples.
    """

    def __init__(self):
        self._records = []

    def _handle(self, msg_type, message):
        """
        Method to be installed using qInstallMsgHandler, stores each message
        into the `messages` attribute.
        """
        if isinstance(message, bytes):
            message = message.decode('utf-8', errors='replace')
        self._records.append(Record(msg_type, message))

    @property
    def records(self):
        """Access messages captured so far.

        :rtype: list of `Record` instances.
        """
        return self._records[:]


class Record(object):
    """Hold information about a message sent by one of Qt log functions.

    :attr str message: message contents.
    :attr Qt.QtMsgType type: enum that identifies message type
    :attr str type_name: `type` as a string
    :attr str log_type_name:
        type name similar to the logging package, for example ``DEBUG``,
        ``WARNING``, etc.
    :attr datetime.datetime when: when the message was sent
    """

    def __init__(self, msg_type, message):
        self._type = msg_type
        self._message = message
        self._type_name = self._get_msg_type_name(msg_type)
        self._log_type_name = self._get_log_type_name(msg_type)
        self._when = datetime.datetime.now()

    message = property(lambda self: self._message)
    type = property(lambda self: self._type)
    type_name = property(lambda self: self._type_name)
    log_type_name = property(lambda self: self._log_type_name)
    when = property(lambda self: self._when)

    @classmethod
    def _get_msg_type_name(cls, msg_type):
        """
        Return a string representation of the given QtMsgType enum
        value.
        """
        if not getattr(cls, '_type_name_map', None):
            cls._type_name_map = {
                QtDebugMsg: 'QtDebugMsg',
                QtWarningMsg: 'QtWarningMsg',
                QtCriticalMsg: 'QtCriticalMsg',
                QtFatalMsg: 'QtFatalMsg',
            }
        return cls._type_name_map[msg_type]

    @classmethod
    def _get_log_type_name(cls, msg_type):
        """
        Return a string representation of the given QtMsgType enum
        value in the same style used by the builtin logging package.
        """
        if not getattr(cls, '_log_type_name_map', None):
            cls._log_type_name_map = {
                QtDebugMsg: 'DEBUG',
                QtWarningMsg: 'WARNING',
                QtCriticalMsg: 'CRITICAL',
                QtFatalMsg: 'FATAL',
            }
        return cls._log_type_name_map[msg_type]
