import dataclasses
from typing import Any


def get_marker(item, name):
    """Get a marker from a pytest item.

    This is here in order to stay compatible with pytest < 3.6 and not produce
    any deprecation warnings with >= 3.6.
    """
    try:
        return item.get_closest_marker(name)
    except AttributeError:
        # pytest < 3.6
        return item.get_marker(name)


@dataclasses.dataclass
class SignalAndArgs:
    signal_name: str
    args: list[Any]

    def __str__(self) -> str:
        args = repr(self.args) if self.args else ""

        # remove signal parameter signature, e.g. turn "some_signal(str,int)" to "some_signal", because we're adding
        # the actual parameters anyways
        signal_name = self.signal_name
        signal_name = signal_name.partition("(")[0]

        return signal_name + args
