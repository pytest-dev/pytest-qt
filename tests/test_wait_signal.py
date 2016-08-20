import functools
import fnmatch

import pytest

from pytestqt.qt_compat import qt_api
from pytestqt.wait_signal import SignalEmittedError


def test_signal_blocker_exception(qtbot):
    """
    Make sure waitSignal without signals and timeout doesn't hang, but raises
    ValueError instead.
    """
    with pytest.raises(ValueError):
        qtbot.waitSignal(None, None).wait()
    with pytest.raises(ValueError):
        qtbot.waitSignals([], None).wait()


def explicit_wait(qtbot, signal, timeout, multiple, raising, should_raise):
    """
    Explicit wait for the signal using blocker API.
    """
    func = qtbot.waitSignals if multiple else qtbot.waitSignal
    blocker = func(signal, timeout, raising=raising)
    assert not blocker.signal_triggered
    if should_raise:
        with pytest.raises(qtbot.SignalTimeoutError):
            blocker.wait()
    else:
        blocker.wait()
    return blocker


def context_manager_wait(qtbot, signal, timeout, multiple, raising,
                         should_raise):
    """
    Waiting for signal using context manager API.
    """
    func = qtbot.waitSignals if multiple else qtbot.waitSignal
    if should_raise:
        with pytest.raises(qtbot.SignalTimeoutError):
            with func(signal, timeout, raising=raising) as blocker:
                pass
    else:
        with func(signal, timeout, raising=raising) as blocker:
            pass
    return blocker


def build_signal_tests_variants(params):
    """
    Helper function to use with pytest's parametrize, to generate additional
    combinations of parameters in a parametrize call:
    - explicit wait and context-manager wait
    - raising True and False (since we check for the correct behavior inside
      each test).
    """
    result = []
    for param in params:
        for wait_function in (explicit_wait, context_manager_wait):
            for raising in (True, False):
                result.append(param + (wait_function, raising))
    return result


@pytest.mark.parametrize(
    ('delay', 'timeout', 'expected_signal_triggered',
     'wait_function', 'raising'),
    build_signal_tests_variants([
        # delay, timeout, expected_signal_triggered
        (200, None, True),
        (200, 400, True),
        (400, 200, False),
    ])
)
def test_signal_triggered(qtbot, timer, stop_watch, wait_function, delay,
                          timeout, expected_signal_triggered, raising,
                          signaller):
    """
    Testing for a signal in different conditions, ensuring we are obtaining
    the expected results.
    """
    timer.single_shot(signaller.signal, delay)

    should_raise = raising and not expected_signal_triggered

    stop_watch.start()
    blocker = wait_function(qtbot, signaller.signal, timeout, raising=raising,
                            should_raise=should_raise, multiple=False)

    # ensure that either signal was triggered or timeout occurred
    assert blocker.signal_triggered == expected_signal_triggered

    stop_watch.check(timeout, delay)


@pytest.mark.parametrize('configval, raises', [
    ('false', False),
    ('true', True),
    (None, True),
])
def test_raising(qtbot, testdir, configval, raises):
    if configval is not None:
        testdir.makeini("""
            [pytest]
            qt_wait_signal_raising = {}
        """.format(configval))

    testdir.makepyfile("""
        import pytest
        from pytestqt.qt_compat import qt_api

        class Signaller(qt_api.QtCore.QObject):
            signal = qt_api.Signal()

        def test_foo(qtbot):
            signaller = Signaller()

            with qtbot.waitSignal(signaller.signal, timeout=10):
                pass
    """)
    res = testdir.runpytest()

    if raises:
        res.stdout.fnmatch_lines(['*1 failed*'])
    else:
        res.stdout.fnmatch_lines(['*1 passed*'])


def test_raising_by_default_overridden(qtbot, testdir):
    testdir.makeini("""
        [pytest]
        qt_wait_signal_raising = false
    """)

    testdir.makepyfile("""
        import pytest
        from pytestqt.qt_compat import qt_api

        class Signaller(qt_api.QtCore.QObject):
            signal = qt_api.Signal()

        def test_foo(qtbot):
            signaller = Signaller()
            signal = signaller.signal

            with qtbot.waitSignal(signal, raising=True, timeout=10) as blocker:
                pass
    """)
    res = testdir.runpytest()
    res.stdout.fnmatch_lines(['*1 failed*'])


@pytest.mark.parametrize(
    ('delay_1', 'delay_2', 'timeout', 'expected_signal_triggered',
     'wait_function', 'raising'),
    build_signal_tests_variants([
        # delay1, delay2, timeout, expected_signal_triggered
        (200, 300, 400, True),
        (300, 200, 400, True),
        (200, 300, None, True),
        (400, 400, 200, False),
        (200, 400, 300, False),
        (400, 200, 200, False),
        (200, 1000, 400, False),
    ])
)
def test_signal_triggered_multiple(qtbot, timer, stop_watch, wait_function,
                                   delay_1, delay_2, timeout, signaller,
                                   expected_signal_triggered, raising):
    """
    Testing for a signal in different conditions, ensuring we are obtaining
    the expected results.
    """
    timer.single_shot(signaller.signal, delay_1)
    timer.single_shot(signaller.signal_2, delay_2)

    should_raise = raising and not expected_signal_triggered

    stop_watch.start()
    blocker = wait_function(qtbot, [signaller.signal, signaller.signal_2],
                            timeout, multiple=True, raising=raising,
                            should_raise=should_raise)

    # ensure that either signal was triggered or timeout occurred
    assert blocker.signal_triggered == expected_signal_triggered

    stop_watch.check(timeout, delay_1, delay_2)


def test_explicit_emit(qtbot, signaller):
    """
    Make sure an explicit emit() inside a waitSignal block works.
    """
    with qtbot.waitSignal(signaller.signal, timeout=5000) as waiting:
        signaller.signal.emit()

    assert waiting.signal_triggered


def test_explicit_emit_multiple(qtbot, signaller):
    """
    Make sure an explicit emit() inside a waitSignal block works.
    """
    with qtbot.waitSignals([signaller.signal, signaller.signal_2],
                           timeout=5000) as waiting:
        signaller.signal.emit()
        signaller.signal_2.emit()

    assert waiting.signal_triggered


@pytest.fixture
def signaller(timer):
    """
    Fixture that provides an object with to signals that can be emitted by
    tests.

    .. note:: we depend on "timer" fixture to ensure that signals emitted
    with "timer" are disconnected before the Signaller() object is destroyed.
    This was the reason for some random crashes experienced on Windows (#80).
    """

    class Signaller(qt_api.QtCore.QObject):
        signal = qt_api.Signal()
        signal_2 = qt_api.Signal()
        signal_args = qt_api.Signal(str, int)
        signal_args_2 = qt_api.Signal(str, int)

    assert timer

    return Signaller()


@pytest.yield_fixture
def timer():
    """
    Fixture that provides a callback with signature: (signal, delay) that
    triggers that signal once after the given delay in ms.

    The fixture is responsible for cleaning up after the timers.
    """

    class Timer(qt_api.QtCore.QObject):
        def __init__(self):
            qt_api.QtCore.QObject.__init__(self)
            self.timers_and_slots = []

        def shutdown(self):
            for t, slot in self.timers_and_slots:
                t.stop()
                t.timeout.disconnect(slot)
            self.timers_and_slots[:] = []

        def single_shot(self, signal, delay):
            t = qt_api.QtCore.QTimer(self)
            t.setSingleShot(True)
            slot = functools.partial(self._emit, signal)
            t.timeout.connect(slot)
            t.start(delay)
            self.timers_and_slots.append((t, slot))

        def _emit(self, signal):
            signal.emit()

    timer = Timer()
    yield timer
    timer.shutdown()


@pytest.mark.parametrize('blocker', ['single', 'multiple', 'callback'])
@pytest.mark.parametrize('raising', [True, False])
def test_blockers_handle_exceptions(qtbot, blocker, raising, signaller):
    """
    Make sure blockers handle exceptions correctly.
    """

    class TestException(Exception):
        pass

    if blocker == 'multiple':
        func = qtbot.waitSignals
        args = [[signaller.signal, signaller.signal_2]]
    elif blocker == 'single':
        func = qtbot.waitSignal
        args = [signaller.signal]
    elif blocker == 'callback':
        func = qtbot.waitCallback
        args = []
    else:
        assert False

    with pytest.raises(TestException):
        with func(*args, timeout=10, raising=raising):
            raise TestException


@pytest.mark.parametrize('multiple', [True, False])
@pytest.mark.parametrize('do_timeout', [True, False])
def test_wait_twice(qtbot, timer, multiple, do_timeout, signaller):
    """
    https://github.com/pytest-dev/pytest-qt/issues/69
    """
    if multiple:
        func = qtbot.waitSignals
        arg = [signaller.signal]
    else:
        func = qtbot.waitSignal
        arg = signaller.signal

    if do_timeout:
        with func(arg, timeout=100, raising=False):
            timer.single_shot(signaller.signal, 200)
        with func(arg, timeout=100, raising=False):
            timer.single_shot(signaller.signal, 200)
    else:
        with func(arg):
            signaller.signal.emit()
        with func(arg):
            signaller.signal.emit()


def test_wait_signals_invalid_strict_parameter(qtbot, signaller):
    with pytest.raises(ValueError):
        qtbot.waitSignals([signaller.signal], order='invalid')


def test_destroyed(qtbot):
    """Test that waitSignal works with the destroyed signal (#82).

    For some reason, this crashes PySide although it seems perfectly fine code.
    """
    if qt_api.pytest_qt_api == 'pyside':
        pytest.skip('test crashes PySide')

    import sip

    class Obj(qt_api.QtCore.QObject):
        pass

    obj = Obj()
    with qtbot.waitSignal(obj.destroyed):
        obj.deleteLater()

    assert sip.isdeleted(obj)


class TestArgs:
    """Try to get the signal arguments from the signal blocker."""

    def test_simple(self, qtbot, signaller):
        """The blocker should store the signal args in an 'args' attribute."""
        with qtbot.waitSignal(signaller.signal_args) as blocker:
            signaller.signal_args.emit('test', 123)
        assert blocker.args == ['test', 123]

    def test_timeout(self, qtbot):
        """If there's a timeout, the args attribute is None."""
        with qtbot.waitSignal(timeout=100, raising=False) as blocker:
            pass
        assert blocker.args is None

    def test_without_args(self, qtbot, signaller):
        """If a signal has no args, the args attribute is an empty list."""
        with qtbot.waitSignal(signaller.signal) as blocker:
            signaller.signal.emit()
        assert blocker.args == []

    def test_multi(self, qtbot, signaller):
        """A MultiSignalBlocker doesn't have an args attribute."""
        with qtbot.waitSignals([signaller.signal]) as blocker:
            signaller.signal.emit()
        with pytest.raises(AttributeError):
            blocker.args

    def test_connected_signal(self, qtbot, signaller):
        """A second signal connected via .connect also works."""
        with qtbot.waitSignal(signaller.signal_args) as blocker:
            blocker.connect(signaller.signal_args_2)
            signaller.signal_args_2.emit('foo', 2342)
        assert blocker.args == ['foo', 2342]


def test_signal_identity(signaller):
    """
    Tests that the identity of signals can be determined correctly, using str(signal).

    Some Qt frameworks, such as PyQt4 or PyQt5, have the following issue:
    x = signaller.signal
    y = signaller.signal
    x == y  # is False

    id(signaller.signal) == id(signaller.signal) # only True because of garbage collection
    between first and second id() call

    id(x) == id(y)  # is False
    str(x) == str(y)  # is True (for all Qt frameworks)
    """
    assert str(signaller.signal) == str(signaller.signal)
    x = signaller.signal
    y = signaller.signal
    assert str(x) == str(y)

    # different signals should also be recognized as different ones
    z = signaller.signal_2
    assert str(x) != str(z)


def get_waitsignals_cases_all(order):
    """
    Returns the list of tuples (emitted-signal-list, expected-signal-list, expect_signal_triggered) for the
    given order parameter of waitSignals().
    """
    cases = get_waitsignals_cases(order, working=True)
    cases.extend(get_waitsignals_cases(order, working=False))
    return cases


def get_waitsignals_cases(order, working):
    """
    Builds combinations for signals to be emitted and expected for working cases (i.e. blocker.signal_triggered == True)
    and non-working cases, depending on the order.

    Note:
    The order ("none", "simple", "strict") becomes stricter from left to right.
    Working cases of stricter cases also work in less stricter cases.
    Non-working cases in less stricter cases also are non-working in stricter cases.
    """
    if order == "none":
        if working:
            cases = get_waitsignals_cases(order="simple", working=True)
            cases.extend([
                # allow even out-of-order signals
                (('A1', 'A2'), ('A2', 'A1'), True),
                (('A1', 'A2'), ('A2', 'Ax'), True),
                (('A1', 'B1'), ('B1', 'A1'), True),
                (('A1', 'B1'), ('B1', 'Ax'), True),
                (('A1', 'B1', 'B1'), ('B1', 'A1', 'B1'), True),
            ])
            return cases
        else:
            return [
                (('A2',), ('A1',), False),
                (('A1',), ('B1',), False),
                (('A1',), ('Bx',), False),
                (('A1', 'A1'), ('A1', 'B1'), False),
                (('A1', 'A1'), ('A1', 'Bx'), False),
                (('A1', 'A1'), ('B1', 'A1'), False),
                (('A1', 'B1'), ('A1', 'A1'), False),
                (('A1', 'B1'), ('B1', 'B1'), False),
                (('A1', 'B1', 'B1'), ('A1', 'A1', 'B1'), False),
            ]
    elif order == "simple":
        if working:
            cases = get_waitsignals_cases(order="strict", working=True)
            cases.extend([
                # allow signals that occur in-between, before or after the expected signals
                (('B1', 'A1', 'A1', 'B1', 'A1'), ('A1', 'B1'), True),
                (('A1', 'A1', 'A1'), ('A1', 'A1'), True),
                (('A1', 'A1', 'A1'), ('A1', 'Ax'), True),
                (('A1', 'A2', 'A1'), ('A1', 'A1'), True),
            ])
            return cases
        else:
            cases = get_waitsignals_cases(order="none", working=False)
            cases.extend([
                # don't allow out-of-order signals
                (('A1', 'B1'), ('B1', 'A1'), False),
                (('A1', 'B1'), ('B1', 'Ax'), False),
                (('A1', 'B1', 'B1'), ('B1', 'A1', 'B1'), False),
                (('A1', 'B1', 'B1'), ('B1', 'B1', 'A1'), False),
            ])
            return cases
    elif order == "strict":
        if working:
            return [
                # only allow exactly the same signals to be emitted that were also expected
                (('A1',), ('A1',), True),
                (('A1',), ('Ax',), True),
                (('A1', 'A1'), ('A1', 'A1'), True),
                (('A1', 'A1'), ('A1', 'Ax'), True),
                (('A1', 'A1'), ('Ax', 'Ax'), True),
                (('A1', 'A2'), ('A1', 'A2'), True),
                (('A2', 'A1'), ('A2', 'A1'), True),
                (('A1', 'B1'), ('A1', 'B1'), True),
                (('A1', 'A1', 'B1'), ('A1', 'A1', 'B1'), True),
                (('A1', 'A2', 'B1'), ('A1', 'A2', 'B1'), True),
                (('A1', 'B1', 'A1'), ('A1', 'A1'), True),  # blocker doesn't know about signal B1 -> test passes
                (('A1', 'B1', 'A1'), ('Ax', 'A1'), True),
            ]
        else:
            cases = get_waitsignals_cases(order="simple", working=False)
            cases.extend([
                # don't allow in-between signals
                (('A1', 'A1', 'A2', 'B1'), ('A1', 'A2', 'B1'), False),
            ])
            return cases


class TestCallback:
    """
    Tests the callback parameter for waitSignal (callbacks in case of waitSignals).
    Uses so-called "signal codes" such as "A1", "B1" or "Ax" which are converted to signals and callback functions.
    The first letter ("A" or "B" is allowed) specifies the signal (signaller.signal_args or signaller.signal_args_2
    respectively), the second letter specifies the parameter to expect or emit ('x' stands for "don't care", i.e. allow
    any value - only applicable for expected signals (not for emitted signals)).
    """

    @staticmethod
    def get_signal_from_code(signaller, code):
        """Converts a code such as 'A1' to a signal (signaller.signal_args for example)."""
        assert type(code) == str and len(code) == 2
        signal = signaller.signal_args if code[0] == 'A' else signaller.signal_args_2
        return signal

    @staticmethod
    def emit_parametrized_signals(signaller, emitted_signal_codes):
        """Emits the signals as specified in the list of emitted_signal_codes using the signaller."""
        for code in emitted_signal_codes:
            signal = TestCallback.get_signal_from_code(signaller, code)
            param_str = code[1]
            assert param_str != "x", "x is not allowed in emitted_signal_codes, only in expected_signal_codes"
            param_int = int(param_str)
            signal.emit(param_str, param_int)

    @staticmethod
    def parameter_evaluation_callback(param_str, param_int, expected_param_str, expected_param_int):
        """
        This generic callback method evaluates that the two provided parameters match the expected ones (which are bound
        using functools.partial).
        """
        return param_str == expected_param_str and param_int == expected_param_int

    @staticmethod
    def parameter_evaluation_callback_accept_any(param_str, param_int):
        return True

    @staticmethod
    def get_signals_and_callbacks(signaller, expected_signal_codes):
        """
        Converts an iterable of strings, such as ('A1', 'A2') to a tuple of the form
        (list of Qt signals, matching parameter-evaluation callbacks)
        Example: ('A1', 'A2') is converted to
        ([signaller.signal_args, signaller.signal_args], [callback(str,int), callback(str,int)]) where the
        first callback expects the values to be '1' and 1, and the second one '2' and 2 respectively.
        I.e. the first character of each signal-code determines the Qt signal, the second one the parameter values.
        """
        signals_to_expect = []
        callbacks = []

        for code in expected_signal_codes:
            # e.g. "A2" means to use signaller.signal_args with parameters "2", 2
            signal = TestCallback.get_signal_from_code(signaller, code)
            signals_to_expect.append(signal)
            param_value_as_string = code[1]
            if param_value_as_string == "x":
                callback = TestCallback.parameter_evaluation_callback_accept_any
            else:
                param_value_as_int = int(param_value_as_string)
                callback = functools.partial(TestCallback.parameter_evaluation_callback,
                                             expected_param_str=param_value_as_string,
                                             expected_param_int=param_value_as_int)
            callbacks.append(callback)

        return signals_to_expect, callbacks

    @pytest.mark.parametrize(
        ('emitted_signal_codes', 'expected_signal_codes', 'expected_signal_triggered'),
        [
            # working cases
            (('A1',), ('A1',), True),
            (('A1',), ('Ax',), True),
            (('A1', 'A1'), ('A1',), True),
            (('A1', 'A2'), ('A1',), True),
            (('A2', 'A1'), ('A1',), True),
            # non working cases
            (('A2',), ('A1',), False),
            (('B1',), ('A1',), False),
            (('A1',), ('Bx',), False),
        ]
    )
    def test_wait_signal(self, qtbot, signaller, emitted_signal_codes, expected_signal_codes,
                         expected_signal_triggered):
        """Tests that waitSignal() correctly checks the signal parameters using the provided callback"""
        signals_to_expect, callbacks = TestCallback.get_signals_and_callbacks(signaller, expected_signal_codes)
        with qtbot.waitSignal(signal=signals_to_expect[0], check_params_cb=callbacks[0], timeout=200,
                              raising=False) as blocker:
            TestCallback.emit_parametrized_signals(signaller, emitted_signal_codes)

        assert blocker.signal_triggered == expected_signal_triggered

    @pytest.mark.parametrize(
        ('emitted_signal_codes', 'expected_signal_codes', 'expected_signal_triggered'),
        get_waitsignals_cases_all(order="none")
    )
    def test_wait_signals_none_order(self, qtbot, signaller, emitted_signal_codes, expected_signal_codes,
                                     expected_signal_triggered):
        """Tests waitSignals() with order="none"."""
        self._test_wait_signals(qtbot, signaller, emitted_signal_codes, expected_signal_codes,
                                expected_signal_triggered, order="none")

    @pytest.mark.parametrize(
        ('emitted_signal_codes', 'expected_signal_codes', 'expected_signal_triggered'),
        get_waitsignals_cases_all(order="simple")
    )
    def test_wait_signals_simple_order(self, qtbot, signaller, emitted_signal_codes, expected_signal_codes,
                                       expected_signal_triggered):
        """Tests waitSignals() with order="simple"."""
        self._test_wait_signals(qtbot, signaller, emitted_signal_codes, expected_signal_codes,
                                expected_signal_triggered, order="simple")

    @pytest.mark.parametrize(
        ('emitted_signal_codes', 'expected_signal_codes', 'expected_signal_triggered'),
        get_waitsignals_cases_all(order="strict")
    )
    def test_wait_signals_strict_order(self, qtbot, signaller, emitted_signal_codes, expected_signal_codes,
                                       expected_signal_triggered):
        """Tests waitSignals() with order="strict"."""
        self._test_wait_signals(qtbot, signaller, emitted_signal_codes, expected_signal_codes,
                                expected_signal_triggered, order="strict")

    @staticmethod
    def _test_wait_signals(qtbot, signaller, emitted_signal_codes, expected_signal_codes,
                           expected_signal_triggered, order):
        signals_to_expect, callbacks = TestCallback.get_signals_and_callbacks(signaller, expected_signal_codes)
        with qtbot.waitSignals(signals=signals_to_expect, order=order, check_params_cbs=callbacks,
                               timeout=200, raising=False) as blocker:
            TestCallback.emit_parametrized_signals(signaller, emitted_signal_codes)

        assert blocker.signal_triggered == expected_signal_triggered

    def test_signals_and_callbacks_length_mismatch(self, qtbot, signaller):
        """
        Tests that a ValueError is raised if the number of expected signals doesn't match the number of provided
        callbacks.
        """
        expected_signal_codes = ('A1', 'A2')
        signals_to_expect, callbacks = TestCallback.get_signals_and_callbacks(signaller, expected_signal_codes)
        callbacks.append(None)
        with pytest.raises(ValueError):
            with qtbot.waitSignals(signals=signals_to_expect, order="none", check_params_cbs=callbacks,
                                   raising=False):
                pass


class TestAssertNotEmitted:
    """Tests for qtbot.assertNotEmitted."""

    def test_not_emitted(self, qtbot, signaller):
        with qtbot.assertNotEmitted(signaller.signal):
            pass

    def test_emitted(self, qtbot, signaller):
        with pytest.raises(SignalEmittedError) as excinfo:
            with qtbot.assertNotEmitted(signaller.signal):
                signaller.signal.emit()

        fnmatch.fnmatchcase(str(excinfo.value),
                            "Signal * unexpectedly emitted.")

    def test_emitted_args(self, qtbot, signaller):
        with pytest.raises(SignalEmittedError) as excinfo:
            with qtbot.assertNotEmitted(signaller.signal_args):
                signaller.signal_args.emit('foo', 123)

        fnmatch.fnmatchcase(str(excinfo.value),
                            "Signal * unexpectedly emitted with arguments "
                            "['foo', 123]")

    def test_disconnected(self, qtbot, signaller):
        with qtbot.assertNotEmitted(signaller.signal):
            pass
        signaller.signal.emit()


class TestWaitCallback:

    def test_immediate(self, qtbot):
        with qtbot.waitCallback() as callback:
            assert not callback.called
            callback()
        assert callback.called

    def test_later(self, qtbot):
        t = QtCore.QTimer()
        t.setSingleShot(True)
        t.setInterval(50)
        with qtbot.waitCallback() as callback:
            t.timeout.connect(callback)
            t.start()
        assert callback.called

    def test_args(self, qtbot):
        with qtbot.waitCallback() as callback:
            callback(23, answer=42)
        assert callback.args == [23]
        assert callback.kwargs == {'answer': 42}

    def test_explicit(self, qtbot):
        blocker = qtbot.waitCallback()
        assert not blocker.called
        blocker()
        blocker.wait()
        assert blocker.called

    # FIXME tests for timeouts
