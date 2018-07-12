import pytest

# noinspection PyUnresolvedReferences
from pytestqt.qt_compat import qt_api


fails_on_pyqt = pytest.mark.xfail('not qt_api.pytest_qt_api.startswith("pyside")')


@pytest.mark.parametrize('expected_method', [
    'keyPress',
    'keyClick',
    'keyClicks',
    'keyEvent',
    'keyPress',
    'keyRelease',
    fails_on_pyqt('keyToAscii'),

    'mouseClick',
    'mouseDClick',
    'mouseMove',
    'mousePress',
    'mouseRelease',
],
)
def test_expected_qtest_proxies(qtbot, expected_method):
    """
    Ensure that we are exporting expected QTest API methods.
    """
    assert hasattr(qtbot, expected_method)
    assert getattr(qtbot, expected_method).__name__ == expected_method
