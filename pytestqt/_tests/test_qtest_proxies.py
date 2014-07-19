import pytest

from pytestqt.qt_compat import USING_PYSIDE


fails_on_pyqt = pytest.mark.xfail(not USING_PYSIDE,
                                  reason='not exported by PyQt')


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
    'mouseEvent',
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