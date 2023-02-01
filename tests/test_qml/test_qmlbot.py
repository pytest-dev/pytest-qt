from pathlib import Path
from textwrap import dedent

import pytest

from pytestqt import QmlBot


def test_load_from_string_wrong_syntax(qmlbot):
    qml = "import QtQuick 2.0 Rectangle{"
    with pytest.raises(RuntimeError):
        qmlbot.loads(qml)


def test_load_from_string(qmlbot: QmlBot) -> None:
    text = "that's a template!"
    qml = dedent(
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


def test_load_from_file(qmlbot: QmlBot) -> None:
    item = qmlbot.load(Path(__file__).parent / "sample.qml")
    assert item.property("hello") == "world"
