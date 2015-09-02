from contextlib import contextmanager
import sys
import traceback


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

    old_hook = sys.excepthook
    sys.excepthook = hook
    try:
        yield result
    finally:
        sys.excepthook = old_hook


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


def _is_exception_capture_disabled(item):
    """returns if exception capture is disabled for the given test item.
    """
    return item.get_marker('qt_no_exception_capture') or \
           item.config.getini('qt_no_exception_capture')