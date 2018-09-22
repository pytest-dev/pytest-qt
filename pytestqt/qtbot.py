import contextlib
import functools
import weakref

from pytestqt.exceptions import SignalTimeoutError, TimeoutError
from pytestqt.qt_compat import qt_api
from pytestqt.wait_signal import (
    SignalBlocker,
    MultiSignalBlocker,
    SignalEmittedSpy,
    SignalEmittedError,
    CallbackBlocker,
    CallbackCalledTwiceError,
)


def _parse_ini_boolean(value):
    if value in (True, False):
        return value
    try:
        return {"true": True, "false": False}[value.lower()]
    except KeyError:
        raise ValueError("unknown string for bool: %r" % value)


class QtBot(object):
    """
    Instances of this class are responsible for sending events to `Qt` objects (usually widgets),
    simulating user input.

    .. important:: Instances of this class should be accessed only by using a ``qtbot`` fixture,
                    never instantiated directly.

    **Widgets**

    .. automethod:: addWidget
    .. automethod:: captureExceptions
    .. automethod:: waitActive
    .. automethod:: waitExposed
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
    .. staticmethod:: mouseMove (widget[, pos=QPoint()[, delay=-1]])
    .. staticmethod:: mousePress (widget, button[, stateKey=0[, pos=QPoint()[, delay=-1]]])
    .. staticmethod:: mouseRelease (widget, button[, stateKey=0[, pos=QPoint()[, delay=-1]]])

        Sends a mouse moves and clicks to a widget.

        :param QWidget widget: the widget that will receive the event

        :param Qt.MouseButton button: flags OR'ed together representing the button pressed.
            Possible flags are:

            * ``Qt.NoButton``: The button state does not refer to any button
              (see QMouseEvent.button()).
            * ``Qt.LeftButton``: The left button is pressed, or an event refers to the left button.
              (The left button may be the right button on left-handed mice.)
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

    def _should_raise(self, raising_arg):
        ini_val = self._request.config.getini("qt_default_raising")
        legacy_ini_val = self._request.config.getini("qt_wait_signal_raising")

        if raising_arg is not None:
            return raising_arg
        elif legacy_ini_val:
            return _parse_ini_boolean(legacy_ini_val)
        elif ini_val:
            return _parse_ini_boolean(ini_val)
        else:
            return True

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

    def waitActive(self, widget, timeout=1000):
        """
        Context manager that waits for ``timeout`` milliseconds or until the window is active.
        If window is not exposed within ``timeout`` milliseconds, raise ``TimeoutError``.

        This is mainly useful for asynchronous systems like X11, where a window will be mapped to screen
        some time after  being asked to show itself on the screen.

        .. code-block:: python

            with qtbot.waitActive(widget, timeout=500):
                show_action()

        :param QWidget widget:
            Widget to wait for.

        :param int|None timeout:
            How many milliseconds to wait for.

        .. note::
            This function is only available in PyQt5, raising a ``RuntimeError`` if called from
            ``PyQt4`` or ``PySide``.

        .. note:: This method is also available as ``wait_active`` (pep-8 alias)
        """
        __tracebackhide__ = True
        return _WaitWidgetContextManager(
            "qWaitForWindowActive", "activated", widget, timeout
        )

    wait_active = waitActive  # pep-8 alias

    def waitExposed(self, widget, timeout=1000):
        """
        Context manager that waits for ``timeout`` milliseconds or until the window is exposed.
        If the window is not exposed within ``timeout`` milliseconds, raise ``TimeoutError``.

        This is mainly useful for asynchronous systems like X11, where a window will be mapped to screen
        some time after  being asked to show itself on the screen.

        .. code-block:: python

            with qtbot.waitExposed(splash, timeout=500):
                startup()

        :param QWidget widget:
            Widget to wait for.

        :param int|None timeout:
            How many milliseconds to wait for.

        .. note::
            This function is only available in PyQt5, raising a ``RuntimeError`` if called from
            ``PyQt4`` or ``PySide``.

        .. note:: This method is also available as ``wait_exposed`` (pep-8 alias)
        """
        __tracebackhide__ = True
        return _WaitWidgetContextManager(
            "qWaitForWindowExposed", "exposed", widget, timeout
        )

    wait_exposed = waitExposed  # pep-8 alias

    def waitForWindowShown(self, widget):
        """
        Waits until the window is shown in the screen. This is mainly useful for asynchronous
        systems like X11, where a window will be mapped to screen some time after being asked to
        show itself on the screen.

        :param QWidget widget:
            Widget to wait on.

        .. note:: In ``PyQt5`` this function is considered deprecated in favor of :meth:`waitExposed`.

        .. note:: This method is also available as ``wait_for_window_shown`` (pep-8 alias)
        """
        if hasattr(qt_api.QtTest.QTest, "qWaitForWindowExposed"):
            return qt_api.QtTest.QTest.qWaitForWindowExposed(widget)
        else:
            return qt_api.QtTest.QTest.qWaitForWindowShown(widget)

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

        qt_api.QApplication.instance().exec_()

        for widget, visible in widget_and_visibility:
            widget.setVisible(visible)

    stop = stopForInteraction

    def waitSignal(self, signal=None, timeout=1000, raising=None, check_params_cb=None):
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

        .. versionadded:: 2.0
           The *check_params_cb* parameter.

        :param Signal signal:
            A signal to wait for, or a tuple ``(signal, signal_name_as_str)`` to improve the error message that is part
            of ``TimeoutError``. Set to ``None`` to just use timeout.
        :param int timeout:
            How many milliseconds to wait before resuming control flow.
        :param bool raising:
            If :class:`QtBot.TimeoutError <pytestqt.plugin.TimeoutError>`
            should be raised if a timeout occurred.
            This defaults to ``True`` unless ``qt_default_raising = false``
            is set in the config.
        :param Callable check_params_cb:
            Optional ``callable`` that compares the provided signal parameters to some expected parameters.
            It has to match the signature of ``signal`` (just like a slot function would) and return ``True`` if
            parameters match, ``False`` otherwise.
        :returns:
            ``SignalBlocker`` object. Call ``SignalBlocker.wait()`` to wait.

        .. note::
            Cannot have both ``signals`` and ``timeout`` equal ``None``, or
            else you will block indefinitely. We throw an error if this occurs.

        .. note::
            This method is also available as ``wait_signal`` (pep-8 alias)
        """
        raising = self._should_raise(raising)
        blocker = SignalBlocker(
            timeout=timeout, raising=raising, check_params_cb=check_params_cb
        )
        if signal is not None:
            blocker.connect(signal)
        return blocker

    wait_signal = waitSignal  # pep-8 alias

    def waitSignals(
        self,
        signals=None,
        timeout=1000,
        raising=None,
        check_params_cbs=None,
        order="none",
    ):
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
            A list of :class:`Signal` objects to wait for. Alternatively: a list of (``Signal, str``) tuples of the form
            ``(signal, signal_name_as_str)`` to improve the error message that is part of ``TimeoutError``.
            Set to ``None`` to just use timeout.
        :param int timeout:
            How many milliseconds to wait before resuming control flow.
        :param bool raising:
            If :class:`QtBot.TimeoutError <pytestqt.plugin.TimeoutError>`
            should be raised if a timeout occurred.
            This defaults to ``True`` unless ``qt_default_raising = false``
            is set in the config.
        :param list check_params_cbs:
            optional list of callables that compare the provided signal parameters to some expected parameters.
            Each callable has to match the signature of the corresponding signal in ``signals`` (just like a slot
            function would) and return ``True`` if parameters match, ``False`` otherwise.
            Instead of a specific callable, ``None`` can be provided, to disable parameter checking for the
            corresponding signal.
            If the number of callbacks doesn't match the number of signals ``ValueError`` will be raised.
        :param str order:
            Determines the order in which to expect signals:

            - ``"none"``: no order is enforced
            - ``"strict"``: signals have to be emitted strictly in the provided order
              (e.g. fails when expecting signals [a, b] and [a, a, b] is emitted)
            - ``"simple"``: like "strict", but signals may be emitted in-between the provided ones, e.g. expected
              ``signals == [a, b, c]`` and actually emitted ``signals = [a, a, b, a, c]`` works
              (would fail with ``"strict"``).

        :returns:
            ``MultiSignalBlocker`` object. Call ``MultiSignalBlocker.wait()``
            to wait.

        .. note::
           Cannot have both ``signals`` and ``timeout`` equal ``None``, or
           else you will block indefinitely. We throw an error if this occurs.

        .. note:: This method is also available as ``wait_signals`` (pep-8 alias)
        """
        if order not in ["none", "simple", "strict"]:
            raise ValueError("order has to be set to 'none', 'simple' or 'strict'")

        raising = self._should_raise(raising)

        if check_params_cbs:
            if len(check_params_cbs) != len(signals):
                raise ValueError(
                    "Number of callbacks ({}) does not "
                    "match number of signals ({})!".format(
                        len(check_params_cbs), len(signals)
                    )
                )
        blocker = MultiSignalBlocker(
            timeout=timeout,
            raising=raising,
            order=order,
            check_params_cbs=check_params_cbs,
        )
        if signals is not None:
            blocker.add_signals(signals)
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
    def assertNotEmitted(self, signal, wait=0):
        """
        .. versionadded:: 1.11

        Make sure the given ``signal`` doesn't get emitted.

        :param int wait:
            How many milliseconds to wait to make sure the signal isn't emitted
            asynchronously. By default, this method returns immediately and only
            catches signals emitted inside the ``with``-block.

        This is intended to be used as a context manager.

        .. note:: This method is also available as ``assert_not_emitted``
                  (pep-8 alias)
        """
        spy = SignalEmittedSpy(signal)
        with spy, self.waitSignal(signal, timeout=wait, raising=False):
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
        so returning an empty list to express "falseness" raises a ``ValueError``.

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
                    msg = "waitUntil() callback must return None, True or False, returned %r"
                    raise ValueError(msg % result)

                # 'assert' form
                if result is None:
                    return

                # 'True/False' form
                if result:
                    return
                else:
                    assert not timed_out(), (
                        "waitUntil timed out in %s miliseconds" % timeout
                    )
            self.wait(10)

    wait_until = waitUntil  # pep-8 alias

    def waitCallback(self, timeout=1000, raising=None):
        """
        .. versionadded:: 3.1

        Stops current test until a callback is called.

        Used to stop the control flow of a test until the returned callback is
        called, or a number of milliseconds, specified by ``timeout``, has
        elapsed.

        Best used as a context manager::

           with qtbot.waitCallback() as callback:
               function_taking_a_callback(callback)
           assert callback.args == [True]

        Also, you can use the :class:`CallbackBlocker` directly if the
        context manager form is not convenient::

           blocker = qtbot.waitCallback(timeout=1000)
           function_calling_a_callback(blocker)
           blocker.wait()


        :param int timeout:
            How many milliseconds to wait before resuming control flow.
        :param bool raising:
            If :class:`QtBot.TimeoutError <pytestqt.plugin.TimeoutError>`
            should be raised if a timeout occurred.
            This defaults to ``True`` unless ``qt_default_raising = false``
            is set in the config.
        :returns:
            A ``CallbackBlocker`` object which can be used directly as a
            callback as it implements ``__call__``.

        .. note:: This method is also available as ``wait_callback`` (pep-8 alias)
        """
        raising = self._should_raise(raising)
        blocker = CallbackBlocker(timeout=timeout, raising=raising)
        return blocker

    wait_callback = waitCallback  # pep-8 alias

    @contextlib.contextmanager
    def captureExceptions(self):
        """
        .. versionadded:: 2.1

        Context manager that captures Qt virtual method exceptions that happen in block inside
        context.

        .. code-block:: python

            with qtbot.capture_exceptions() as exceptions:
                qtbot.click(button)

            # exception is a list of sys.exc_info tuples
            assert len(exceptions) == 1

        .. note:: This method is also available as ``capture_exceptions`` (pep-8 alias)
        """
        from pytestqt.exceptions import capture_exceptions

        with capture_exceptions() as exceptions:
            yield exceptions

    capture_exceptions = captureExceptions

    @classmethod
    def _inject_qtest_methods(cls):
        """
        Injects QTest methods into the given class QtBot, so the user can access
        them directly without having to import QTest.
        """

        def create_qtest_proxy_method(method_name):

            if hasattr(qt_api.QtTest.QTest, method_name):
                qtest_method = getattr(qt_api.QtTest.QTest, method_name)

                def result(*args, **kwargs):
                    return qtest_method(*args, **kwargs)

                functools.update_wrapper(result, qtest_method)
                return staticmethod(result)
            else:
                return None  # pragma: no cover

        # inject methods from QTest into QtBot
        method_names = [
            "keyPress",
            "keyClick",
            "keyClicks",
            "keyEvent",
            "keyPress",
            "keyRelease",
            "keyToAscii",
            "mouseClick",
            "mouseDClick",
            "mouseMove",
            "mousePress",
            "mouseRelease",
        ]
        for method_name in method_names:
            method = create_qtest_proxy_method(method_name)
            if method is not None:
                setattr(cls, method_name, method)


# provide easy access to exceptions to qtbot fixtures
QtBot.SignalTimeoutError = SignalTimeoutError
QtBot.SignalEmittedError = SignalEmittedError
QtBot.TimeoutError = TimeoutError
QtBot.CallbackCalledTwiceError = CallbackCalledTwiceError


def _add_widget(item, widget):
    """
    Register a widget into the given pytest item for later closing.
    """
    qt_widgets = getattr(item, "qt_widgets", [])
    qt_widgets.append(weakref.ref(widget))
    item.qt_widgets = qt_widgets


def _close_widgets(item):
    """
    Close all widgets registered in the pytest item.
    """
    widgets = getattr(item, "qt_widgets", None)
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
    return iter(getattr(item, "qt_widgets", []))


class _WaitWidgetContextManager(object):
    """
    Context manager implementation used by ``waitActive`` and ``waitExposed`` methods.
    """

    def __init__(self, method_name, adjective_name, widget, timeout):
        """
        :param str method_name: name ot the ``QtTest`` method to call to check if widget is active/exposed.
        :param str adjective_name: "activated" or "exposed".
        :param widget:
        :param timeout:
        """
        self._method_name = method_name
        self._adjective_name = adjective_name
        self._widget = widget
        self._timeout = timeout

    def __enter__(self):
        __tracebackhide__ = True
        if qt_api.pytest_qt_api != "pyqt5":
            raise RuntimeError("Available in PyQt5 only")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        __tracebackhide__ = True
        try:
            if exc_type is None:
                method = getattr(qt_api.QtTest.QTest, self._method_name)
                r = method(self._widget, self._timeout)
                if not r:
                    msg = "widget {} not {} in {} ms.".format(
                        self._widget, self._adjective_name, self._timeout
                    )
                    raise TimeoutError(msg)
        finally:
            self._widget = None
