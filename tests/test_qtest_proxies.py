import pytest

# noinspection PyUnresolvedReferences
from pytestqt.qt_compat import qt_api


fails_on_pyqt = pytest.mark.xfail(
    qt_api.pytest_qt_api == "pyqt5", reason="fails on PyQt"
)

keysequence = pytest.mark.skipif(
    not hasattr(qt_api.QtTest.QTest, "keySequence"), reason="needs Qt >= 5.10"
)


@pytest.mark.parametrize(
    "expected_method",
    [
        "keyPress",
        "keyClick",
        "keyClicks",
        "keyEvent",
        "keyPress",
        "keyRelease",
        pytest.param("keyToAscii", marks=fails_on_pyqt),
        pytest.param("keySequence", marks=keysequence),
        "mouseClick",
        "mouseDClick",
        "mouseMove",
        "mousePress",
        "mouseRelease",
    ],
)
def test_expected_qtest_proxies(qtbot, expected_method):
    """
    Ensure that we are exporting expected QTest API methods.
    """
    assert hasattr(qtbot, expected_method)
    assert getattr(qtbot, expected_method).__name__ == expected_method
