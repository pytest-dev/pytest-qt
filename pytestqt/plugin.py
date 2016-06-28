import pytest

from pytestqt.exceptions import capture_exceptions, format_captured_exceptions, \
    _is_exception_capture_enabled, _QtExceptionCaptureManager
from pytestqt.logging import QtLoggingPlugin, _QtMessageCapture, Record
from pytestqt.qt_compat import QApplication, QT_API
from pytestqt.qtbot import QtBot, _close_widgets
from pytestqt.wait_signal import SignalBlocker, MultiSignalBlocker, SignalTimeoutError

# classes/functions imported here just for backward compatibility before we
# split the implementation of this file in several modules
assert QtBot
assert SignalBlocker
assert MultiSignalBlocker
assert SignalTimeoutError
assert Record
assert capture_exceptions
assert format_captured_exceptions


@pytest.yield_fixture(scope='session')
def qapp():
    """
    fixture that instantiates the QApplication instance that will be used by
    the tests.
    """
    from pytestqt.qt_compat import QApplication
    app = QApplication.instance()
    if app is None:
        global _qapp_instance
        _qapp_instance = QApplication([])
        yield _qapp_instance
    else:
        yield app  # pragma: no cover

# holds a global QApplication instance created in the qapp fixture; keeping
# this reference alive avoids it being garbage collected too early
_qapp_instance = None


@pytest.fixture
def qtbot(qapp, request):
    """
    Fixture used to create a QtBot instance for using during testing.

    Make sure to call addWidget for each top-level widget you create to ensure
    that they are properly closed after the test ends.
    """
    result = QtBot(request)
    return result


@pytest.fixture
def qtlog(request):
    """Fixture that can access messages captured during testing"""
    if hasattr(request._pyfuncitem, 'qt_log_capture'):
        return request._pyfuncitem.qt_log_capture
    else:
        return _QtMessageCapture([])  # pragma: no cover


@pytest.yield_fixture
def qtmodeltester(request):
    """
    Fixture used to create a ModelTester instance to test models.
    """
    from pytestqt.modeltest import ModelTester
    tester = ModelTester(request.config)
    yield tester
    tester._cleanup()


def pytest_addoption(parser):
    parser.addini('qt_no_exception_capture',
                  'disable automatic exception capture')
    parser.addini('qt_wait_signal_raising',
                  'Default value for the raising parameter of qtbot.waitSignal')

    default_log_fail = QtLoggingPlugin.LOG_FAIL_OPTIONS[0]
    parser.addini('qt_log_level_fail',
                  'log level in which tests can fail: {0} (default: "{1}")'
                  .format(QtLoggingPlugin.LOG_FAIL_OPTIONS, default_log_fail),
                  default=default_log_fail)
    parser.addini('qt_log_ignore',
                  'list of regexes for messages that should not cause a tests '
                  'to fails', type='linelist')

    group = parser.getgroup('qt', 'qt testing')
    group.addoption('--no-qt-log', dest='qt_log', action='store_false',
                    default=True, help='disable pytest-qt logging capture')
    if QT_API == 'pyqt5':
        default = '{rec.context.file}:{rec.context.function}:' \
                  '{rec.context.line}:\n    {rec.type_name}: {rec.message}'
    else:
        default = '{rec.type_name}: {rec.message}'
    group.addoption('--qt-log-format', dest='qt_log_format', default=default,
                    help='defines how qt log messages are displayed, '
                         'default: "{0}"'.format(default))


@pytest.mark.hookwrapper
@pytest.mark.tryfirst
def pytest_runtest_setup(item):
    """
    Hook called after before test setup starts, to start capturing exceptions
    as early as possible.
    """
    capture_enabled = _is_exception_capture_enabled(item)
    if capture_enabled:
        item.qt_exception_capture_manager = _QtExceptionCaptureManager()
        item.qt_exception_capture_manager.start()
    yield
    _process_events()
    if capture_enabled:
        item.qt_exception_capture_manager.fail_if_exceptions_occurred('SETUP')


@pytest.mark.hookwrapper
@pytest.mark.tryfirst
def pytest_runtest_call(item):
    yield
    _process_events()
    capture_enabled = _is_exception_capture_enabled(item)
    if capture_enabled:
        item.qt_exception_capture_manager.fail_if_exceptions_occurred('CALL')


@pytest.mark.hookwrapper
@pytest.mark.trylast
def pytest_runtest_teardown(item):
    """
    Hook called after each test tear down, to process any pending events and
    avoiding leaking events to the next test. Also, if exceptions have
    been captured during fixtures teardown, fail the test.
    """
    _process_events()
    _close_widgets(item)
    _process_events()
    yield
    _process_events()
    capture_enabled = _is_exception_capture_enabled(item)
    if capture_enabled:
        item.qt_exception_capture_manager.fail_if_exceptions_occurred('TEARDOWN')
        item.qt_exception_capture_manager.finish()


def _process_events():
    """Calls app.processEvents() while taking care of capturing exceptions
    or not based on the given item's configuration.
    """
    app = QApplication.instance()
    if app is not None:
        app.processEvents()


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        "qt_no_exception_capture: Disables pytest-qt's automatic exception "
        'capture for just one test item.')

    config.addinivalue_line(
        'markers',
        'qt_log_level_fail: overrides qt_log_level_fail ini option.')
    config.addinivalue_line(
        'markers',
        'qt_log_ignore: overrides qt_log_ignore ini option.')

    if config.getoption('qt_log'):
        config.pluginmanager.register(QtLoggingPlugin(config), '_qt_logging')


def pytest_report_header():
    from pytestqt.qt_compat import get_versions
    v = get_versions()
    fields = [
        '%s %s' % (v.qt_api, v.qt_api_version),
        'Qt runtime %s' % v.runtime,
        'Qt compiled %s' % v.compiled,
    ]
    version_line = ' -- '.join(fields)
    return [version_line]




