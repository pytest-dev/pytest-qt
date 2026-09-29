import pathlib

import pytest

from pytestqt.qt_compat import qt_api
from pytestqt.qtbot import QtBot, QWidget


@pytest.fixture
def widget(qtbot: QtBot) -> QWidget:
    w = qt_api.QtWidgets.QWidget()
    qtbot.addWidget(w)
    w.setAttribute(qt_api.QtCore.Qt.WidgetAttribute.WA_StyledBackground)
    w.setStyleSheet("background-color: magenta")
    return w


def test_basic(qtbot: QtBot, widget: QWidget) -> None:
    path = qtbot.screenshot(widget)
    assert path.exists()

    pixmap = qt_api.QtGui.QPixmap()
    assert pixmap.load(str(path))

    image = pixmap.toImage()
    color = image.pixelColor(image.rect().center())
    assert (color.red(), color.green(), color.blue()) == (255, 0, 255)


def test_region(qtbot: QtBot, widget: QWidget) -> None:
    region = qt_api.QtCore.QRect(0, 0, 25, 25)
    path = qtbot.screenshot(widget, region=region)

    pixmap = qt_api.QtGui.QPixmap()
    assert pixmap.load(str(path))
    assert pixmap.rect() == region


def test_filename_class(qtbot: QtBot, widget: QWidget) -> None:
    path = qtbot.screenshot(widget)
    assert path.name == "screenshot_QWidget.png"


def test_filename_objectname(qtbot: QtBot, widget: QWidget) -> None:
    widget.setObjectName("shotgun")
    path = qtbot.screenshot(widget)
    assert path.name == "screenshot_QWidget_shotgun.png"


def test_filename_suffix(qtbot: QtBot, widget: QWidget) -> None:
    path = qtbot.screenshot(widget, suffix="before")
    assert path.name == "screenshot_QWidget_before.png"


def test_filename_both(qtbot: QtBot, widget: QWidget) -> None:
    widget.setObjectName("shotgun")
    path = qtbot.screenshot(widget, suffix="before")
    assert path.name == "screenshot_QWidget_shotgun_before.png"


def test_filename_endless(
    qtbot: QtBot, widget: QWidget, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pathlib.Path, "exists", lambda _self: True)
    with pytest.raises(qtbot.ScreenshotError, match="Failed to find unique filename"):
        qtbot.screenshot(widget, suffix="before")


def test_filename_invalid(qtbot: QtBot, widget: QWidget) -> None:
    with pytest.raises(qtbot.ScreenshotError, match="Saving to .* failed"):
        qtbot.screenshot(widget, suffix=r"invalid/path\everywhere")


def test_folder(qtbot: QtBot, tmp_path: pathlib.Path, widget: QWidget) -> None:
    path = qtbot.screenshot(widget)
    assert path.parent == tmp_path


@pytest.mark.parametrize(
    "existing, expected",
    [
        (["QLineEdit"], "QWidget"),
        (["QWidget"], "QWidget_2"),
        (["QWidget_2"], "QWidget"),
        (["QWidget", "QWidget_2"], "QWidget_3"),
    ],
)
def test_filename_dedup(
    qtbot: QtBot,
    widget: QWidget,
    tmp_path: pathlib.Path,
    existing: list[str],
    expected: str,
) -> None:
    for name in existing:
        path = tmp_path / f"screenshot_{name}.png"
        path.touch()

    path = qtbot.screenshot(widget)
    assert path.name == f"screenshot_{expected}.png"
