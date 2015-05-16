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
    res = testdir.runpytest('--qt-log-format={}'.format(f))
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
