from typing import TYPE_CHECKING

from pytestqt.exceptions import SignalEmittedError
from pytestqt.utils import SignalAndArgs as SignalAndArgs
if TYPE_CHECKING:
    from pytestqt.wait_signal_impl import (
        SignalBlocker as SignalBlocker,
        MultiSignalBlocker as MultiSignalBlocker,
        CallbackBlocker as CallbackBlocker,
    )


def __getattr__(name: str) -> type:
    """Avoid importing wait_signal_impl at the top level as qt_api is uninitialized."""
    from pytestqt.wait_signal_impl import (
        SignalBlocker,
        MultiSignalBlocker,
        CallbackBlocker,
    )
    if name == "SignalBlocker":
        return SignalBlocker
    elif name == "MultiSignalBlocker":
        return MultiSignalBlocker
    elif name == "CallbackBlocker":
        return CallbackBlocker
    else:
        raise AttributeError(f"module {__name__} has no attribute {name}")


class SignalEmittedSpy:
    """
    .. versionadded:: 1.11

    An object which checks if a given signal has ever been emitted.

    Intended to be used as a context manager.
    """

    def __init__(self, signal):
        self.signal = signal
        self.emitted = False
        self.args = None

    def slot(self, *args):
        self.emitted = True
        self.args = args

    def __enter__(self):
        self.signal.connect(self.slot)

    def __exit__(self, type, value, traceback):
        self.signal.disconnect(self.slot)

    def assert_not_emitted(self):
        if self.emitted:
            if self.args:
                raise SignalEmittedError(
                    "Signal %r unexpectedly emitted with "
                    "arguments %r" % (self.signal, list(self.args))
                )
            else:
                raise SignalEmittedError(f"Signal {self.signal!r} unexpectedly emitted")
