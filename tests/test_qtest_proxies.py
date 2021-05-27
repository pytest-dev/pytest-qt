import pytest

from pytestqt.qt_compat import qt_api


@pytest.mark.parametrize(
    "expected_method",
    [
        "keyPress",
        "keyClick",
        "keyClicks",
        "keyEvent",
        "keyPress",
        "keyRelease",
        "keyToAscii",
        "keySequence",
        "mouseClick",
        "mouseDClick",
        "mouseMove",
        "mousePress",
        "mouseRelease",
    ],
)
def test_expected_qtest_proxies(qtbot, expected_method):
    """
    This test originates from the implementation where QTest
    API methods were exported on runtime.
    """
    assert hasattr(qtbot, expected_method)
    assert getattr(qtbot, expected_method).__name__ == expected_method


@pytest.mark.skipif(qt_api.is_pyside, reason="PyQt test only")
def test_keyToAscii_not_available_on_pyqt(testdir):
    """
    Test that qtbot.keyToAscii() is not available on PyQt5 and
    calling the method raises a NotImplementedError.
    """
    testdir.makepyfile(
        """
        import pytest
        from pytestqt.qt_compat import qt_api

        def test_foo(qtbot):
            widget = qt_api.QtWidgets.QWidget()
            qtbot.add_widget(widget)
            with pytest.raises(NotImplementedError):
                qtbot.keyToAscii(qt_api.QtCore.Qt.Key.Key_Escape)
        """
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(["*= 1 passed in *"])
