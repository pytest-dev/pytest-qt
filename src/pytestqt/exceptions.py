from __future__ import annotations

import functools
import inspect
import sys
import traceback
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from types import FrameType, TracebackType
from typing import Optional

import pytest
from typing_extensions import Unpack
from pytestqt.utils import get_marker

CapturedException = tuple[type[BaseException], BaseException, Optional[TracebackType]]
CapturedExceptions = list[CapturedException]
ExceptHook = Callable[[Unpack[CapturedException]], object]


@contextmanager
def capture_exceptions() -> Iterator[CapturedExceptions]:
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


def _except_hook(
    type_: type[BaseException],
    value: BaseException,
    tback: TracebackType | None,
    exceptions: CapturedExceptions,
) -> None:
    """Hook functions installed by _QtExceptionCaptureManager"""
    exceptions.append((type_, value, tback))
    sys.stderr.write(format_captured_exceptions([(type_, value, tback)]))


class _QtExceptionCaptureManager:
    """
    Manages exception capture context.
    """

    def __init__(self) -> None:
        self.old_hook: ExceptHook | None = None
        self.exceptions: CapturedExceptions = []

    def start(self) -> None:
        """Start exception capturing by installing a hook into sys.excepthook
        that records exceptions received into ``self.exceptions``.
        """
        self.old_hook = sys.excepthook
        sys.excepthook = functools.partial(_except_hook, exceptions=self.exceptions)

    def finish(self) -> None:
        """Stop exception capturing, restoring the original hook.

        Can be called multiple times.
        """
        if self.old_hook is not None:
            sys.excepthook = self.old_hook
            self.old_hook = None

    def fail_if_exceptions_occurred(self, when: str) -> None:
        """Re-raise captured exceptions so pytest formats the traceback.

        Stops capturing first. Nothing happens when no exception was captured.
        """
        __tracebackhide__ = True
        if not self.exceptions:
            return
        self.finish()
        exceptions = self.exceptions
        self.exceptions = []
        try:
            _reraise_captured_exceptions(exceptions, when)
        finally:
            del exceptions[:]  # Don't keep exceptions alive longer (#187).
            if hasattr(sys, "last_exc"):
                sys.last_exc = None  # type: ignore[assignment]


def _reraise_captured_exceptions(exceptions: CapturedExceptions, when: str) -> None:
    """Raise captured event-loop exceptions with their original tracebacks.

    pytest then prints them with the usual traceback style. Several independent
    exceptions are chained so each one is still reported.
    """
    __tracebackhide__ = True
    note = f"caught in Qt event loop during {when.lower()}"
    prepared = [
        _prepare_captured_exception(value, tb, note) for _, value, tb in exceptions
    ]
    current = prepared[0]
    for extra in prepared[1:]:
        current = _chain_independent_exceptions(current, extra)
    # Drop frame locals so Qt objects referenced there can be collected (#187).
    # Source lines still come from the code objects.
    _clear_exception_locals(current)
    raise current


def _prepare_captured_exception(
    value: BaseException, tb: TracebackType | None, note: str
) -> BaseException:
    if tb is not None:
        value = value.with_traceback(tb)
    # KeyboardInterrupt would abort the session; report it as a test failure.
    if isinstance(value, KeyboardInterrupt):
        replacement = RuntimeError(note)
        replacement.__cause__ = value
        replacement.__suppress_context__ = True
        return replacement
    _add_note(value, note)
    return value


def _add_note(exc: BaseException, note: str) -> None:
    add_note = getattr(exc, "add_note", None)
    if add_note is None:
        return
    existing = getattr(exc, "__notes__", ())
    if note not in existing:
        add_note(note)


def _clear_exception_locals(exc: BaseException | None) -> None:
    """Clear locals on captured frames so Qt objects can be collected (#187).

    A traceback frame's ``f_back`` still points at the finished test frame,
    which is what keeps the widget alive. Leave frames that are still running
    alone.
    """
    executing: set[FrameType] = set()
    frame = inspect.currentframe()
    while frame is not None:
        executing.add(frame)
        frame = frame.f_back
    _clear_exception_locals_rec(exc, set(), set(), executing)


def _clear_exception_locals_rec(
    exc: BaseException | None,
    seen_excs: set[int],
    seen_frames: set[int],
    executing: set[FrameType],
) -> None:
    if exc is None or id(exc) in seen_excs:
        return
    seen_excs.add(id(exc))
    tb = exc.__traceback__
    while tb is not None:
        frame: FrameType | None = tb.tb_frame
        while frame is not None and id(frame) not in seen_frames:
            seen_frames.add(id(frame))
            if frame not in executing:
                frame.clear()
            frame = frame.f_back
        tb = tb.tb_next
    _clear_exception_locals_rec(exc.__cause__, seen_excs, seen_frames, executing)
    _clear_exception_locals_rec(exc.__context__, seen_excs, seen_frames, executing)
    group = getattr(exc, "exceptions", None)
    if group:
        for sub in group:
            _clear_exception_locals_rec(sub, seen_excs, seen_frames, executing)


def _chain_independent_exceptions(
    earlier: BaseException, later: BaseException
) -> BaseException:
    """Attach ``earlier`` to ``later`` without dropping an existing chain."""
    if later.__context__ is None and not later.__suppress_context__:
        later.__context__ = earlier
        later.__suppress_context__ = False
        return later
    carrier = RuntimeError("Another exception caught in Qt event loop")
    carrier.__cause__ = later
    carrier.__suppress_context__ = True
    carrier.__context__ = earlier
    return carrier


def format_captured_exceptions(exceptions: CapturedExceptions) -> str:
    """
    Formats exceptions given as (type, value, traceback) into a string
    suitable to display as a test failure.
    """
    from io import StringIO

    stream = StringIO()
    stream.write("Exceptions caught in Qt event loop:\n")
    sep = "_" * 80 + "\n"
    stream.write(sep)
    for exc_type, value, tback in exceptions:
        traceback.print_exception(exc_type, value, tback, file=stream)
        stream.write(sep)
    return stream.getvalue()


def _is_exception_capture_enabled(item: pytest.Item) -> bool:
    """returns if exception capture is disabled for the given test item."""
    disabled = get_marker(item, "qt_no_exception_capture") or item.config.getini(
        "qt_no_exception_capture"
    )
    return not disabled


class TimeoutError(Exception):
    """
    .. versionadded:: 2.1

    Exception thrown by :class:`pytestqt.qtbot.QtBot` methods.

    Access via ``qtbot.TimeoutError``.
    """


class ScreenshotError(Exception):
    """
    .. versionadded:: 4.1

    Exception thrown by :meth:`pytestqt.qtbot.QtBot.screenshot` if taking the
    screenshot failed.

    .. versionchanged:: 4.2

        Access via ``qtbot.ScreenshotError``.
    """
