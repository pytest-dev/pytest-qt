from pathlib import Path

import pytest


def test_load_from_string_wrong_syntax(qmlbot):
    qml = "import QtQuick 2.0 Rectangle{"
    with pytest.raises(RuntimeError):
        qmlbot.loads(qml)


def test_load_from_string(qmlbot: pytestqt.QmlBot) -> None:
    text = "that's a template!"
    qml = (
        """
import QtQuick 2.0

Rectangle{
    objectName: "sample";
    property string hello: "%s"
}
"""
        % text
    )
    item = qmlbot.loads(qml)
    assert item.property("hello") == text


def test_load_from_file(qmlbot):
    item = qmlbot.load(Path(__file__).parent / "sample.qml")
    assert item.property("hello") == "world"
