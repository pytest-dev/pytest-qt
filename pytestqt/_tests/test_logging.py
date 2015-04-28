import pytest

pytest_plugins = 'pytester'


@pytest.mark.parametrize('test_succeds, qt_log',
                         [(True, True), (True, False), (False, False),
                          (False, True)])
def test_basic_logging(testdir, test_succeds, qt_log):
    """
    :type testdir: _pytest.pytester.TmpTestdir
    """
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qDebug, qWarning, qCritical, qFatal

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
