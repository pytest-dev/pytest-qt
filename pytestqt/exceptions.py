from contextlib import contextmanager
import sys
import traceback
import pytest


@contextmanager
def capture_exceptions():
    """
    Context manager that captures exceptions that happen insides its context,
    and returns them as a list of (type, value, traceback) after the
    context ends.
    """
    manager = _QtExceptionCaptureManager()
    manager.start()
    try:
        yield manager.exceptions
    finally:
        manager.finish()


class _QtExceptionCaptureManager(object):
    """
    Manages exception capture context.
    """

    def __init__(self):
        self.old_hook = None
        self.exceptions = []

    def start(self):
        """Start exception capturing by installing a hook into sys.excepthook
        that records exceptions received into ``self.exceptions``.
        """
        def hook(type_, value, tback):
            self.exceptions.append((type_, value, tback))
            sys.stderr.write(format_captured_exceptions([(type_, value, tback)]))

        self.old_hook = sys.excepthook
        sys.excepthook = hook

    def finish(self):
        """Stop exception capturing, restoring the original hook.

        Can be called multiple times.
        """
        if self.old_hook is not None:
            sys.excepthook = self.old_hook
            self.old_hook = None

    def fail_if_exceptions_occurred(self, when):
        """calls pytest.fail() with an informative message if exceptions
        have been captured so far. Before pytest.fail() is called, also
        finish capturing.
        """
        if self.exceptions:
            self.finish()
            exceptions = self.exceptions
            self.exceptions = []
            prefix = '%s ERROR: ' % when
            pytest.fail(prefix + format_captured_exceptions(exceptions),
                        pytrace=False)


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


def _is_exception_capture_enabled(item):
    """returns if exception capture is disabled for the given test item.
    """
    disabled = item.get_marker('qt_no_exception_capture') or \
               item.config.getini('qt_no_exception_capture')
    return not disabled


class TimeoutError(Exception):
    """
    .. versionadded:: 2.1

    Exception thrown by :class:`pytestqt.qtbot.QtBot` methods.

    .. note::
        In versions prior to ``2.1``, this exception was called ``SignalTimeoutError``.
        An alias is kept for backward compatibility.
    """
    pass


# backward compatibility alias
SignalTimeoutError = TimeoutError
