import functools
import contextlib
import weakref
from pytestqt.wait_signal import SignalBlocker, MultiSignalBlocker, SignalTimeoutError, \
    SignalEmittedSpy
from pytestqt.qt_compat import QtTest, QApplication


def _parse_ini_boolean(value):
    if value in (True, False):
        return value
    try:
        return {'true': True, 'false': False}[value.lower()]
    except KeyError:
        raise ValueError('unknown string for bool: %r' % value)


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
    .. automethod:: wait

    **Signals and Events**

    .. automethod:: waitSignal
    .. automethod:: waitSignals
    .. automethod:: assertNotEmitted
    .. automethod:: waitUntil

    **Raw QTest API**

    Methods below provide very low level functions, as sending a single mouse click or a key event.
    Those methods are just forwarded directly to the `QTest API`_. Consult the documentation for more
    information.

    ---

    Below are methods used to simulate sending key events to widgets:

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

        .. note:: This method is not available in PyQt.

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

    def __init__(self, request):
        self._request = request

    def addWidget(self, widget):
        """
        Adds a widget to be tracked by this bot. This is not required, but will ensure that the
        widget gets closed by the end of the test, so it is highly recommended.

        :param QWidget widget:
            Widget to keep track of.

        .. note:: This method is also available as ``add_widget`` (pep-8 alias)
        """
        _add_widget(self._request.node, widget)

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

        .. note:: This method is also available as ``wait_for_window_shown`` (pep-8 alias)
        """
        if hasattr(QtTest.QTest, 'qWaitForWindowShown'):  # pragma: no cover
            # PyQt4 and PySide
            QtTest.QTest.qWaitForWindowShown(widget)
        else:  # pragma: no cover
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
        for weak_widget in _iter_widgets(self._request.node):
            widget = weak_widget()
            if widget is not None:
                widget_and_visibility.append((widget, widget.isVisible()))

        QApplication.instance().exec_()

        for widget, visible in widget_and_visibility:
            widget.setVisible(visible)

    stop = stopForInteraction

    def waitSignal(self, signal=None, timeout=1000, raising=None):
        """
        .. versionadded:: 1.2

        Stops current test until a signal is triggered.

        Used to stop the control flow of a test until a signal is emitted, or
        a number of milliseconds, specified by ``timeout``, has elapsed.

        Best used as a context manager::

           with qtbot.waitSignal(signal, timeout=1000):
               long_function_that_calls_signal()

        Also, you can use the :class:`SignalBlocker` directly if the context
        manager form is not convenient::

           blocker = qtbot.waitSignal(signal, timeout=1000)
           blocker.connect(another_signal)
           long_function_that_calls_signal()
           blocker.wait()

        Any additional signal, when triggered, will make :meth:`wait` return.

        .. versionadded:: 1.4
           The *raising* parameter.

        :param Signal signal:
            A signal to wait for. Set to ``None`` to just use timeout.
        :param int timeout:
            How many milliseconds to wait before resuming control flow.
        :param bool raising:
            If :class:`QtBot.SignalTimeoutError <pytestqt.plugin.SignalTimeoutError>`
            should be raised if a timeout occurred.
            This defaults to ``True`` unless ``qt_wait_signal_raising = false``
            is set in the config.
        :returns:
            ``SignalBlocker`` object. Call ``SignalBlocker.wait()`` to wait.

        .. note::
           Cannot have both ``signals`` and ``timeout`` equal ``None``, or
           else you will block indefinitely. We throw an error if this occurs.

        .. note:: This method is also available as ``wait_signal`` (pep-8 alias)
        """
        if raising is None:
            raising_val = self._request.config.getini('qt_wait_signal_raising')
            if not raising_val:
                raising = True
            else:
                raising = _parse_ini_boolean(raising_val)
        blocker = SignalBlocker(timeout=timeout, raising=raising)
        if signal is not None:
            blocker.connect(signal)
        return blocker

    wait_signal = waitSignal  # pep-8 alias

    def waitSignals(self, signals=None, timeout=1000, raising=None):
        """
        .. versionadded:: 1.4

        Stops current test until all given signals are triggered.

        Used to stop the control flow of a test until all (and only
        all) signals are emitted or the number of milliseconds specified by
        ``timeout`` has elapsed.

        Best used as a context manager::

           with qtbot.waitSignals([signal1, signal2], timeout=1000):
               long_function_that_calls_signals()

        Also, you can use the :class:`MultiSignalBlocker` directly if the
        context manager form is not convenient::

           blocker = qtbot.waitSignals(signals, timeout=1000)
           long_function_that_calls_signal()
           blocker.wait()

        :param list signals:
            A list of :class:`Signal` objects to wait for. Set to ``None`` to
            just use timeout.
        :param int timeout:
            How many milliseconds to wait before resuming control flow.
        :param bool raising:
            If :class:`QtBot.SignalTimeoutError <pytestqt.plugin.SignalTimeoutError>`
            should be raised if a timeout occurred.
            This defaults to ``True`` unless ``qt_wait_signal_raising = false``
            is set in the config.
        :returns:
            ``MultiSignalBlocker`` object. Call ``MultiSignalBlocker.wait()``
            to wait.

        .. note::
           Cannot have both ``signals`` and ``timeout`` equal ``None``, or
           else you will block indefinitely. We throw an error if this occurs.

        .. note:: This method is also available as ``wait_signals`` (pep-8 alias)
        """
        if raising is None:
            raising = self._request.config.getini('qt_wait_signal_raising')
        blocker = MultiSignalBlocker(timeout=timeout, raising=raising)
        if signals is not None:
            for signal in signals:
                blocker._add_signal(signal)
        return blocker

    wait_signals = waitSignals  # pep-8 alias

    def wait(self, ms):
        """
        .. versionadded:: 1.9

        Waits for ``ms`` milliseconds.

        While waiting, events will be processed and your test will stay
        responsive to user interface events or network communication.
        """
        blocker = MultiSignalBlocker(timeout=ms, raising=False)
        blocker.wait()

    @contextlib.contextmanager
    def assertNotEmitted(self, signal):
        """
        .. versionadded:: 1.11

        Make sure the given ``signal`` doesn't get emitted.

        This is intended to be used as a context manager.

        .. note:: This method is also available as ``assert_not_emitted``
                  (pep-8 alias)
        """
        spy = SignalEmittedSpy(signal)
        with spy:
            yield
        spy.assert_not_emitted()

    assert_not_emitted = assertNotEmitted  # pep-8 alias

    def waitUntil(self, callback, timeout=1000):
        """
        .. versionadded:: 2.0

        Wait in a busy loop, calling the given callback periodically until timeout is reached.

        ``callback()`` should raise ``AssertionError`` to indicate that the desired condition
        has not yet been reached, or just return ``None`` when it does. Useful to ``assert`` until
        some condition is satisfied:

        .. code-block:: python

            def view_updated():
                assert view_model.count() > 10
            qtbot.waitUntil(view_updated)

        Another possibility is for ``callback()`` to return ``True`` when the desired condition
        is met, ``False`` otherwise. Useful specially with ``lambda`` for terser code, but keep
        in mind that the error message in those cases is usually not very useful because it is
        not using an ``assert`` expression.

        .. code-block:: python

            qtbot.waitUntil(lambda: view_model.count() > 10)

        Note that this usage only accepts returning actual ``True`` and ``False`` values,
        so returning an empty list to express "falseness" raises an ``ValueError``.

        :param callback: callable that will be called periodically.
        :param timeout: timeout value in ms.
        :raises ValueError: if the return value from the callback is anything other than ``None``,
            ``True`` or ``False``.

        .. note:: This method is also available as ``wait_until`` (pep-8 alias)
        """
        __tracebackhide__ = True
        import time
        start = time.time()

        def timed_out():
            elapsed = time.time() - start
            elapsed_ms = elapsed * 1000
            return elapsed_ms > timeout

        while True:
            try:
                result = callback()
            except AssertionError:
                if timed_out():
                    raise
            else:
                if result not in (None, True, False):
                    msg = 'waitUntil() callback must return None, True or False, returned %r'
                    raise ValueError(msg % result)

                # 'assert' form
                if result is None:
                    return

                # 'True/False' form
                if result:
                    return
                else:
                    assert not timed_out(), 'waitUntil timed out in %s miliseconds' % timeout
            self.wait(10)

    wait_until = waitUntil  # pep-8 alias


# provide easy access to SignalTimeoutError to qtbot fixtures
QtBot.SignalTimeoutError = SignalTimeoutError


def _add_widget(item, widget):
    """
    Register a widget into the given pytest item for later closing.
    """
    qt_widgets = getattr(item, 'qt_widgets', [])
    qt_widgets.append(weakref.ref(widget))
    item.qt_widgets = qt_widgets


def _close_widgets(item):
    """
    Close all widgets registered in the pytest item.
    """
    widgets = getattr(item, 'qt_widgets', None)
    if widgets:
        for w in item.qt_widgets:
            w = w()
            if w is not None:
                w.close()
                w.deleteLater()
        del item.qt_widgets


def _iter_widgets(item):
    """
    Iterates over widgets registered in the given pytest item.
    """
    return iter(getattr(item, 'qt_widgets', []))
