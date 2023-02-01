import os
from pathlib import Path
from typing import Any

from pytestqt.qt_compat import qt_api


class QmlBot:
    def __init__(self) -> None:
        self.engine = qt_api.QtQml.QQmlApplicationEngine()
        main = Path(__file__).parent / "botloader.qml"
        self.engine.load(os.fspath(main))

    @property
    def _loader(self) -> Any:
        self._root = self.engine.rootObjects()[
            0
        ]  # self is needed for it not to be collected by the gc
        return self._root.findChild(qt_api.QtQuick.QQuickItem, "contentloader")

    def load(self, path: Path) -> Any:
        """
        :returns: `QQuickItem` - the initialized component
        """
        self._loader.setProperty("source", path.resolve(True).as_uri())
        return self._loader.property("item")

    def loads(self, content: str) -> Any:
        """
        :returns: `QQuickItem` - the initialized component
        """
        self._comp = qt_api.QtQml.QQmlComponent(
            self.engine
        )  # needed for it not to be collected by the gc
        self._comp.setData(content.encode("utf-8"), qt_api.QtCore.QUrl())
        if self._comp.status() != qt_api.QtQml.QQmlComponent.Status.Ready:
            raise RuntimeError(
                f"component {self._comp} is not Ready:\n"
                f"STATUS: {self._comp.status()}\n"
                f"HINT: make sure there are no wrong spaces.\n"
                f"ERRORS: {self._comp.errors()}"
            )
        self._loader.setProperty("source", "")
        self._loader.setProperty("sourceComponent", self._comp)
        return self._loader.property("item")
