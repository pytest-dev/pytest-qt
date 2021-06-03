import datetime

import pytest

from pytestqt.qt_compat import qt_api


@pytest.mark.parametrize("test_succeeds", [True, False])
@pytest.mark.parametrize("qt_log", [True, False])
def test_basic_logging(testdir, test_succeeds, qt_log):
    """
    Test Qt logging capture output.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makepyfile(
        """
        import sys
        from pytestqt.qt_compat import qt_api

        def to_unicode(s):
            return s.decode('utf-8', 'replace') if isinstance(s, bytes) else s

        def print_msg(msg_type, context, message):
            sys.stderr.write(to_unicode(message) + '\\n')
        qt_api.QtCore.qInstallMessageHandler(print_msg)

        def test_types():
            # qInfo is not exposed by the bindings yet (#225)
            # qt_api.qInfo('this is an INFO message')
            qt_api.qDebug('this is a DEBUG message')
            qt_api.qWarning('this is a WARNING message')
            qt_api.qCritical('this is a CRITICAL message')
            assert {}
        """.format(
            test_succeeds
        )
    )
    res = testdir.runpytest(*(["--no-qt-log"] if not qt_log else []))
    if test_succeeds:
        assert "Captured Qt messages" not in res.stdout.str()
        assert "Captured stderr call" not in res.stdout.str()
    else:
        if qt_log:
            res.stdout.fnmatch_lines(
                [
                    "*-- Captured Qt messages --*",
                    # qInfo is not exposed by the bindings yet (#232)
                    # '*QtInfoMsg: this is an INFO message*',
                    "*QtDebugMsg: this is a DEBUG message*",
                    "*QtWarningMsg: this is a WARNING message*",
                    "*QtCriticalMsg: this is a CRITICAL message*",
                ]
            )
        else:
            res.stdout.fnmatch_lines(
                [
                    "*-- Captured stderr call --*",
                    # qInfo is not exposed by the bindings yet (#232)
                    # '*QtInfoMsg: this is an INFO message*',
                    # 'this is an INFO message*',
                    "this is a DEBUG message*",
                    "this is a WARNING message*",
                    "this is a CRITICAL message*",
                ]
            )


def test_qinfo(qtlog):
    """Test INFO messages when we have means to do so. Should be temporary until bindings
    catch up and expose qInfo (or at least QMessageLogger), then we should update
    the other logging tests properly. #232
    """

    if qt_api.is_pyside:
        assert (
            qt_api.qInfo is None
        ), "pyside2/6 does not expose qInfo. If it does, update this test."
        return

    qt_api.qInfo("this is an INFO message")
    records = [(m.type, m.message.strip()) for m in qtlog.records]
    assert records == [(qt_api.QtCore.QtMsgType.QtInfoMsg, "this is an INFO message")]


def test_qtlog_fixture(qtlog):
    """
    Test qtlog fixture.
    """
    # qInfo is not exposed by the bindings yet (#232)
    qt_api.qDebug("this is a DEBUG message")
    qt_api.qWarning("this is a WARNING message")
    qt_api.qCritical("this is a CRITICAL message")
    records = [(m.type, m.message.strip()) for m in qtlog.records]
    assert records == [
        (qt_api.QtCore.QtMsgType.QtDebugMsg, "this is a DEBUG message"),
        (qt_api.QtCore.QtMsgType.QtWarningMsg, "this is a WARNING message"),
        (qt_api.QtCore.QtMsgType.QtCriticalMsg, "this is a CRITICAL message"),
    ]
    # `records` attribute is read-only
    with pytest.raises(AttributeError):
        qtlog.records = []


@pytest.mark.parametrize("arg", ["--no-qt-log", "--capture=no", "-s"])
def test_fixture_with_logging_disabled(testdir, arg):
    """
    Test that qtlog fixture doesn't capture anything if logging is disabled
    in the command line.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api

        def test_types(qtlog):
            qt_api.qWarning('message')
            assert qtlog.records == []
        """
    )
    res = testdir.runpytest(arg)
    res.stdout.fnmatch_lines("*1 passed*")


@pytest.mark.parametrize("use_context_manager", [True, False])
def test_disable_qtlog_context_manager(testdir, use_context_manager):
    """
    Test qtlog.disabled() context manager.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makeini(
        """
        [pytest]
        qt_log_level_fail = CRITICAL
        """
    )

    if use_context_manager:
        code = "with qtlog.disabled():"
    else:
        code = "if 1:"

    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api
        def test_1(qtlog):
            {code}
                qt_api.qCritical('message')
        """.format(
            code=code
        )
    )
    res = testdir.inline_run()
    passed = 1 if use_context_manager else 0
    res.assertoutcome(passed=passed, failed=int(not passed))


@pytest.mark.parametrize("use_mark", [True, False])
def test_disable_qtlog_mark(testdir, use_mark):
    """
    Test mark which disables logging capture for a test.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makeini(
        """
        [pytest]
        qt_log_level_fail = CRITICAL
        """
    )
    mark = "@pytest.mark.no_qt_log" if use_mark else ""

    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api
        import pytest
        {mark}
        def test_1():
            qt_api.qCritical('message')
        """.format(
            mark=mark
        )
    )
    res = testdir.inline_run()
    passed = 1 if use_mark else 0
    res.assertoutcome(passed=passed, failed=int(not passed))


def test_logging_formatting(testdir):
    """
    Test custom formatting for logging messages.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api
        def test_types():
            qt_api.qWarning('this is a WARNING message')
            assert 0
        """
    )
    f = "{rec.type_name} {rec.log_type_name} {rec.when:%Y-%m-%d}: {rec.message}"
    res = testdir.runpytest(f"--qt-log-format={f}")
    today = "{:%Y-%m-%d}".format(datetime.datetime.now())
    res.stdout.fnmatch_lines(
        [
            "*-- Captured Qt messages --*",
            f"QtWarningMsg WARNING {today}: this is a WARNING message*",
        ]
    )


@pytest.mark.parametrize(
    "level, expect_passes", [("DEBUG", 1), ("WARNING", 2), ("CRITICAL", 3), ("NO", 4)]
)
def test_logging_fails_tests(testdir, level, expect_passes):
    """
    Test qt_log_level_fail ini option.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makeini(
        """
        [pytest]
        qt_log_level_fail = {level}
        """.format(
            level=level
        )
    )
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api
        def test_1():
            qt_api.qDebug('this is a DEBUG message')
        def test_2():
            qt_api.qWarning('this is a WARNING message')
        def test_3():
            qt_api.qCritical('this is a CRITICAL message')
        def test_4():
            assert 1
        """
    )
    res = testdir.runpytest()
    lines = []
    if level != "NO":
        lines.extend(
            [
                "*Failure: Qt messages with level {} or above emitted*".format(
                    level.upper()
                ),
                "*-- Captured Qt messages --*",
            ]
        )
    lines.append(f"*{expect_passes} passed*")
    res.stdout.fnmatch_lines(lines)


def test_logging_fails_tests_mark(testdir):
    """
    Test mark overrides what's configured in the ini file.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makeini(
        """
        [pytest]
        qt_log_level_fail = CRITICAL
        """
    )
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qWarning
        import pytest
        @pytest.mark.qt_log_level_fail('WARNING')
        def test_1():
            qWarning('message')
        """
    )
    res = testdir.inline_run()
    res.assertoutcome(failed=1)


def test_logging_fails_ignore(testdir):
    """
    Test qt_log_ignore config option.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makeini(
        """
        [pytest]
        qt_log_level_fail = CRITICAL
        qt_log_ignore =
            WM_DESTROY.*sent
            WM_PAINT not handled
        """
    )
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api
        import pytest

        def test1():
            qt_api.qCritical('a critical message')
        def test2():
            qt_api.qCritical('WM_DESTROY was sent')
        def test3():
            qt_api.qCritical('WM_DESTROY was sent')
            assert 0
        def test4():
            qt_api.qCritical('WM_PAINT not handled')
            qt_api.qCritical('another critical message')
        """
    )
    res = testdir.runpytest()
    lines = [
        # test1 fails because it has emitted a CRITICAL message and that message
        # does not match any regex in qt_log_ignore
        "*_ test1 _*",
        "*Failure: Qt messages with level CRITICAL or above emitted*",
        "*QtCriticalMsg: a critical message*",
        # test2 succeeds because its message matches qt_log_ignore
        # test3 fails because of an assert, but the ignored message should
        # still appear in the failure message
        "*_ test3 _*",
        "*AssertionError*",
        "*QtCriticalMsg: WM_DESTROY was sent*(IGNORED)*",
        # test4 fails because one message is ignored but the other isn't
        "*_ test4 _*",
        "*Failure: Qt messages with level CRITICAL or above emitted*",
        "*QtCriticalMsg: WM_PAINT not handled*(IGNORED)*",
        "*QtCriticalMsg: another critical message*",
        # summary
        "*3 failed, 1 passed*",
    ]
    res.stdout.fnmatch_lines(lines)


@pytest.mark.parametrize("message", ["match-global", "match-mark"])
@pytest.mark.parametrize("marker_args", ["'match-mark', extend=True", "'match-mark'"])
def test_logging_mark_with_extend(testdir, message, marker_args):
    """
    Test qt_log_ignore mark with extend=True.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makeini(
        """
        [pytest]
        qt_log_level_fail = CRITICAL
        qt_log_ignore = match-global
        """
    )
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api
        import pytest

        @pytest.mark.qt_log_ignore({marker_args})
        def test1():
            qt_api.qCritical('{message}')
        """.format(
            message=message, marker_args=marker_args
        )
    )
    res = testdir.inline_run()
    res.assertoutcome(passed=1, failed=0)


@pytest.mark.parametrize(
    "message, error_expected", [("match-global", True), ("match-mark", False)]
)
def test_logging_mark_without_extend(testdir, message, error_expected):
    """
    Test qt_log_ignore mark with extend=False.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makeini(
        """
        [pytest]
        qt_log_level_fail = CRITICAL
        qt_log_ignore = match-global
        """
    )
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api
        import pytest

        @pytest.mark.qt_log_ignore('match-mark', extend=False)
        def test1():
            qt_api.qCritical('{message}')
        """.format(
            message=message
        )
    )
    res = testdir.inline_run()

    if error_expected:
        res.assertoutcome(passed=0, failed=1)
    else:
        res.assertoutcome(passed=1, failed=0)


def test_logging_mark_with_invalid_argument(testdir):
    """
    Test qt_log_ignore mark with invalid keyword argument.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makepyfile(
        """
        import pytest

        @pytest.mark.qt_log_ignore('match-mark', does_not_exist=True)
        def test1():
            pass
        """
    )
    res = testdir.runpytest()
    lines = [
        "*= ERRORS =*",
        "*_ ERROR at setup of test1 _*",
        "*ValueError: Invalid keyword arguments in {'does_not_exist': True} "
        "for qt_log_ignore mark.",
        # summary
        "*= 1 error in*",
    ]
    res.stdout.fnmatch_lines(lines)


@pytest.mark.parametrize("apply_mark", [True, False])
def test_logging_fails_ignore_mark_multiple(testdir, apply_mark):
    """
    Make sure qt_log_ignore mark supports multiple arguments.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    if apply_mark:
        mark = '@pytest.mark.qt_log_ignore("WM_DESTROY", "WM_PAINT")'
    else:
        mark = ""
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api
        import pytest
        @pytest.mark.qt_log_level_fail('CRITICAL')
        {mark}
        def test1():
            qt_api.qCritical('WM_PAINT was sent')
        """.format(
            mark=mark
        )
    )
    res = testdir.inline_run()
    passed = 1 if apply_mark else 0
    res.assertoutcome(passed=passed, failed=int(not passed))


def test_lineno_failure(testdir):
    """
    Test that tests when failing because log messages were emitted report
    the correct line number.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makeini(
        """
        [pytest]
        qt_log_level_fail = WARNING
        """
    )
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api
        def test_foo():
            assert foo() == 10
        def foo():
            qt_api.qWarning('this is a WARNING message')
            return 10
        """
    )
    res = testdir.runpytest()
    if qt_api.is_pyqt:
        res.stdout.fnmatch_lines(
            [
                "*test_lineno_failure.py:2: Failure*",
                "*test_lineno_failure.py:foo:5:*",
                "    QtWarningMsg: this is a WARNING message",
            ]
        )
    else:
        res.stdout.fnmatch_lines(
            [
                "*test_lineno_failure.py:2: Failure*",
                "QtWarningMsg: this is a WARNING message",
            ]
        )


def test_context_none(testdir):
    """
    Sometimes PyQt will emit a context with some/all attributes set as None
    instead of appropriate file, function and line number.

    Test that when this happens the plugin doesn't break, and it filters
    out the context information.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api

        def test_foo(request):
            log_capture = request.node.qt_log_capture
            context = log_capture._Context(None, None, 0, None)
            log_capture._handle_with_context(qt_api.QtCore.QtMsgType.QtWarningMsg,
                                             context, "WARNING message")
            assert 0
        """
    )
    res = testdir.runpytest()
    assert "*None:None:0:*" not in str(res.stdout)
    res.stdout.fnmatch_lines(["QtWarningMsg: WARNING message"])


def test_logging_broken_makereport(testdir):
    """
    Make sure logging's makereport hookwrapper doesn't hide exceptions.

    See https://github.com/pytest-dev/pytest-qt/issues/98

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makepyfile(
        conftest="""
        import pytest

        @pytest.mark.hookwrapper(tryfirst=True)
        def pytest_runtest_makereport(call):
            if call.when == 'call':
                raise Exception("This should not be hidden")
            yield
    """
    )
    p = testdir.makepyfile(
        """
        def test_foo():
            pass
        """
    )
    res = testdir.runpytest_subprocess(p)
    res.stdout.fnmatch_lines(["*This should not be hidden*"])
