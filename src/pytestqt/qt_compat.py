"""
Provide a common way to import Qt classes used by pytest-qt in a unique manner,
abstracting API differences between PyQt5 and PySide2/6.

.. note:: This module is not part of pytest-qt public API, hence its interface
may change between releases and users should not rely on it.

Based on from https://github.com/epage/PythonUtils.
"""


from collections import namedtuple
import os


VersionTuple = namedtuple("VersionTuple", "qt_api, qt_api_version, runtime, compiled")


def _import(name):
    """Think call so we can mock it during testing"""
    return __import__(name)


class _QtApi:
    """
    Interface to the underlying Qt API currently configured for pytest-qt.

    This object lazily loads all class references and other objects when the ``set_qt_api`` method
    gets called, providing a uniform way to access the Qt classes.
    """

    def __init__(self):
        self._import_errors = {}

    def _get_qt_api_from_env(self):
        api = os.environ.get("PYTEST_QT_API")
        if api is not None:
            api = api.lower()
            if api not in (
                "pyside6",
                "pyside2",
                "pyqt5",
            ):  # pragma: no cover
                msg = "Invalid value for $PYTEST_QT_API: %s"
                raise RuntimeError(msg % api)
        return api

    def _guess_qt_api(self):  # pragma: no cover
        def _can_import(name):
            try:
                _import(name)
                return True
            except ModuleNotFoundError as e:
                self._import_errors[name] = str(e)
                return False

        # Note, not importing only the root namespace because when uninstalling from conda,
        # the namespace can still be there.
        if _can_import("PySide6.QtCore"):
            return "pyside6"
        elif _can_import("PySide2.QtCore"):
            return "pyside2"
        elif _can_import("PyQt5.QtCore"):
            return "pyqt5"
        return None

    def set_qt_api(self, api):
        self.pytest_qt_api = self._get_qt_api_from_env() or api or self._guess_qt_api()

        self.is_pyside = self.pytest_qt_api in ["pyside2", "pyside6"]

        if not self.pytest_qt_api:  # pragma: no cover
            errors = "\n".join(
                f"  {module}: {reason}"
                for module, reason in sorted(self._import_errors.items())
            )
            msg = (
                "pytest-qt requires either PySide2, PySide6 or PyQt5 installed.\n"
                + errors
            )
            raise RuntimeError(msg)

        _root_modules = {
            "pyside6": "PySide6",
            "pyside2": "PySide2",
            "pyqt5": "PyQt5",
        }
        _root_module = _root_modules[self.pytest_qt_api]

        def _import_module(module_name):
            m = __import__(_root_module, globals(), locals(), [module_name], 0)
            return getattr(m, module_name)

        self.QtCore = QtCore = _import_module("QtCore")
        self.QtGui = QtGui = _import_module("QtGui")
        self.QtTest = _import_module("QtTest")
        self.Qt = QtCore.Qt
        self.QEvent = QtCore.QEvent

        # qInfo is not exposed in PySide2/6 (#232)
        if hasattr(QtCore, "QMessageLogger"):
            self.qInfo = lambda msg: QtCore.QMessageLogger().info(msg)
        elif hasattr(QtCore, "qInfo"):
            self.qInfo = QtCore.qInfo
        else:
            self.qInfo = None

        self.qDebug = QtCore.qDebug
        self.qWarning = QtCore.qWarning
        self.qCritical = QtCore.qCritical
        self.qFatal = QtCore.qFatal
        self.QtInfoMsg = getattr(QtCore, "QtInfoMsg", None)
        self.QtDebugMsg = QtCore.QtDebugMsg
        self.QtWarningMsg = QtCore.QtWarningMsg
        self.QtCriticalMsg = QtCore.QtCriticalMsg
        self.QtFatalMsg = QtCore.QtFatalMsg

        if self.is_pyside:
            self.Signal = QtCore.Signal
            self.Slot = QtCore.Slot
            self.Property = QtCore.Property
            if hasattr(QtGui, "QStringListModel"):
                self.QStringListModel = QtGui.QStringListModel
            else:
                self.QStringListModel = QtCore.QStringListModel

            self.QStandardItem = QtGui.QStandardItem
            self.QStandardItemModel = QtGui.QStandardItemModel
            self.QAbstractListModel = QtCore.QAbstractListModel
            self.QAbstractTableModel = QtCore.QAbstractTableModel

            _QtWidgets = _import_module("QtWidgets")
            self.QApplication = _QtWidgets.QApplication
            self.QWidget = _QtWidgets.QWidget
            self.QLineEdit = _QtWidgets.QLineEdit
            self.qInstallMessageHandler = QtCore.qInstallMessageHandler

            self.QSortFilterProxyModel = QtCore.QSortFilterProxyModel
        elif self.pytest_qt_api == "pyqt5":
            self.Signal = QtCore.pyqtSignal
            self.Slot = QtCore.pyqtSlot
            self.Property = QtCore.pyqtProperty

            _QtWidgets = _import_module("QtWidgets")
            self.QApplication = _QtWidgets.QApplication
            self.QWidget = _QtWidgets.QWidget
            self.qInstallMessageHandler = QtCore.qInstallMessageHandler

            self.QStringListModel = QtCore.QStringListModel
            self.QSortFilterProxyModel = QtCore.QSortFilterProxyModel

            self.QStandardItem = QtGui.QStandardItem
            self.QStandardItemModel = QtGui.QStandardItemModel
            self.QAbstractListModel = QtCore.QAbstractListModel
            self.QAbstractTableModel = QtCore.QAbstractTableModel

    def get_versions(self):
        if self.pytest_qt_api == "pyside6":
            import PySide6

            version = PySide6.__version__

            return VersionTuple(
                "PySide6", version, self.QtCore.qVersion(), self.QtCore.__version__
            )
            pass
        elif self.pytest_qt_api == "pyside2":
            import PySide2

            version = PySide2.__version__

            return VersionTuple(
                "PySide2", version, self.QtCore.qVersion(), self.QtCore.__version__
            )
        else:
            return VersionTuple(
                "PyQt5",
                self.QtCore.PYQT_VERSION_STR,
                self.QtCore.qVersion(),
                self.QtCore.QT_VERSION_STR,
            )


qt_api = _QtApi()
