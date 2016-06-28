import pytest
import time
import sys

pytest_plugins = 'pytester'


@pytest.fixture
def stop_watch():
    """
    Fixture that makes it easier for tests to ensure signals emitted and
    timeouts are being respected.
    """
    # time.clock() is more accurate on Windows
    get_time = time.clock if sys.platform.startswith('win') else time.time

    class StopWatch:

        def __init__(self):
            self._start_time = None
            self.elapsed = None

        def start(self):
            self._start_time = get_time()

        def stop(self):
            self.elapsed = (get_time() - self._start_time) * 1000.0

        def check(self, timeout, *delays):
            """
            Make sure either timeout (if given) or at most of the given
            delays used to trigger a signal has passed.
            """
            self.stop()
            if timeout is None:
                timeout = max(delays) * 1.35  # 35% tolerance
            max_wait_ms = max(delays + (timeout,))
            assert self.elapsed < max_wait_ms

    return StopWatch()
