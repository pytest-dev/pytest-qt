import datetime

import pytest

from pytestqt.qt_compat import qDebug, qWarning, qCritical, QtDebugMsg, \
    QtWarningMsg, QtCriticalMsg

pytest_plugins = 'pytester'


@pytest.mark.parametrize('test_succeds, qt_log',
                         [(True, True), (True, False), (False, False),
                          (False, True)])
def test_basic_logging(testdir, test_succeds, qt_log):
    """
    Test Qt logging capture output.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qDebug, qWarning, qCritical

        def test_types():
            qDebug('this is a DEBUG message')
            qWarning('this is a WARNING message')
            qCritical('this is a CRITICAL message')
            assert {0}
        """.format(test_succeds)
    )
    res = testdir.runpytest(*(['--no-qt-log'] if not qt_log else []))
    if test_succeds:
        assert 'Captured Qt messages' not in res.stdout.str()
        assert 'Captured stderr call' not in res.stdout.str()
    else:
        if qt_log:
            res.stdout.fnmatch_lines([
                '*-- Captured Qt messages --*',
                'QtDebugMsg: this is a DEBUG message*',
                'QtWarningMsg: this is a WARNING message*',
                'QtCriticalMsg: this is a CRITICAL message*',
            ])
        else:
            res.stdout.fnmatch_lines([
                '*-- Captured stderr call --*',
                'this is a DEBUG message*',
                'this is a WARNING message*',
                'this is a CRITICAL message*',
            ])


def test_qtlog_fixture(qtlog):
    """
    Test qtlog fixture.
    """
    qDebug('this is a DEBUG message')
    qWarning('this is a WARNING message')
    qCritical('this is a CRITICAL message')
    records = [(m.type, m.message.strip()) for m in qtlog.records]
    assert records == [
        (QtDebugMsg, 'this is a DEBUG message'),
        (QtWarningMsg, 'this is a WARNING message'),
        (QtCriticalMsg, 'this is a CRITICAL message'),
    ]
    # `records` attribute is read-only
    with pytest.raises(AttributeError):
        qtlog.records = []


def test_fixture_with_logging_disabled(testdir):
    """
    Test that qtlog fixture doesn't capture anything if logging is disabled
    in the command line.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qWarning

        def test_types(qtlog):
            qWarning('message')
            assert qtlog.records == []
        """
    )
    res = testdir.runpytest('--no-qt-log')
    res.stdout.fnmatch_lines('*1 passed*')


def test_logging_formatting(testdir):
    """
    Test custom formatting for logging messages.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qWarning
        def test_types():
            qWarning('this is a WARNING message')
            assert 0
        """
    )
    f = '{rec.type_name} {rec.log_type_name} {rec.when:%Y-%m-%d}: {rec.message}'
    res = testdir.runpytest('--qt-log-format={0}'.format(f))
    today = '{0:%Y-%m-%d}'.format(datetime.datetime.now())
    res.stdout.fnmatch_lines([
        '*-- Captured Qt messages --*',
        'QtWarningMsg WARNING {0}: this is a WARNING message*'.format(today),
    ])


@pytest.mark.parametrize('level, expect_passes',
                         [('DEBUG', 1), ('WARNING', 2), ('CRITICAL', 3),
                          ('NO', 4)],
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
        """.format(level=level)
    )
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qWarning, qCritical, qDebug
        def test_1():
            qDebug('this is a DEBUG message')
        def test_2():
            qWarning('this is a WARNING message')
        def test_3():
            qCritical('this is a CRITICAL message')
        def test_4():
            assert 1
        """
    )
    res = testdir.runpytest()
    lines = []
    if level != 'NO':
        lines.extend([
            '*Failure: Qt messages with level {0} or above emitted*'.format(
                level.upper()),
            '*-- Captured Qt messages --*',
        ])
    lines.append('*{0} passed*'.format(expect_passes))
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
        from pytestqt.qt_compat import qWarning, qCritical, qDebug
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
        from pytestqt.qt_compat import qWarning, qCritical
        import pytest

        def test1():
            qCritical('a critical message')
        def test2():
            qCritical('WM_DESTROY was sent')
        def test3():
            qCritical('WM_DESTROY was sent')
            assert 0
        def test4():
            qCritical('WM_PAINT not handled')
            qCritical('another critical message')
        """
    )
    res = testdir.runpytest()
    lines = [
        # test1 fails because it has emitted a CRITICAL message and that message
        # does not match any regex in qt_log_ignore
        '*_ test1 _*',
        '*Failure: Qt messages with level CRITICAL or above emitted*',
        '*QtCriticalMsg: a critical message*',

        # test2 succeeds because its message matches qt_log_ignore

        # test3 fails because of an assert, but the ignored message should
        # still appear in the failure message
        '*_ test3 _*',
        '*AssertionError*',
        '*QtCriticalMsg: WM_DESTROY was sent*(IGNORED)*',

        # test4 fails because one message is ignored but the other isn't
        '*_ test4 _*',
        '*Failure: Qt messages with level CRITICAL or above emitted*',
        '*QtCriticalMsg: WM_PAINT not handled*(IGNORED)*',
        '*QtCriticalMsg: another critical message*',

        # summary
        '*3 failed, 1 passed*',
    ]
    res.stdout.fnmatch_lines(lines)


@pytest.mark.parametrize('mark_regex', ['WM_DESTROY.*sent', 'no-match', None])
def test_logging_fails_ignore_mark(testdir, mark_regex):
    """
    Test qt_log_ignore mark overrides config option.

    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makeini(
        """
        [pytest]
        qt_log_level_fail = CRITICAL
        """
    )
    if mark_regex:
        mark = '@pytest.mark.qt_log_ignore("{0}")'.format(mark_regex)
    else:
        mark = ''
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qWarning, qCritical
        import pytest
        {mark}
        def test1():
            qCritical('WM_DESTROY was sent')
        """.format(mark=mark)
    )
    res = testdir.inline_run()
    passed = 1 if mark_regex == 'WM_DESTROY.*sent' else 0
    res.assertoutcome(passed=passed, failed=int(not passed))
