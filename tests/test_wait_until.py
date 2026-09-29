from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Optional

import pytest

from pytestqt.qt_compat import qt_api
from pytestqt.qtbot import QtBot


class Counter:
    """
    Counts timer "ticks" periodically.
    """

    def __init__(self) -> None:
        self._ticks = 0
        self.timer = qt_api.QtCore.QTimer()
        self.timer.timeout.connect(self._tick)

    def start(self, ms: int) -> None:
        self.timer.start(ms)

    def _tick(self) -> None:
        self._ticks += 1

    @property
    def ticks(self) -> int:
        return self._ticks


def test_wait_until(
    qtbot: QtBot,
    wait_4_ticks_callback: Callable[[], Optional[bool]],
    tick_counter: Counter,
) -> None:
    tick_counter.start(100)
    qtbot.waitUntil(wait_4_ticks_callback, timeout=1000)
    assert tick_counter.ticks >= 4


def test_wait_until_timeout(
    qtbot: QtBot,
    wait_4_ticks_callback: Callable[[], Optional[bool]],
    tick_counter: Counter,
) -> None:
    tick_counter.start(200)
    with pytest.raises(qtbot.TimeoutError):
        qtbot.waitUntil(wait_4_ticks_callback, timeout=100)
    assert tick_counter.ticks < 4


def test_invalid_callback_return_value(qtbot: QtBot) -> None:
    with pytest.raises(ValueError):
        qtbot.waitUntil(lambda: [])  # type: ignore[arg-type,return-value]


def test_pep8_alias(qtbot: QtBot) -> None:
    qtbot.wait_until


@pytest.fixture(params=["predicate", "assert"])
def wait_4_ticks_callback(
    request: pytest.FixtureRequest, tick_counter: Counter
) -> Callable[[], Optional[bool]]:
    """Parametrized fixture which returns the two possible callback methods that can be
    passed to ``waitUntil``: predicate and assertion.
    """
    if request.param == "predicate":
        return lambda: tick_counter.ticks >= 4
    else:

        def check_ticks() -> None:
            assert tick_counter.ticks >= 4

        return check_ticks


@pytest.fixture
def tick_counter() -> Iterator[Counter]:
    """
    Returns an object which counts timer "ticks" periodically.
    """
    counter = Counter()
    yield counter
    counter.timer.stop()
