"""
Provide a common way to import Qt classes used by pytest-qt in a unique manner,
abstracting API differences between PyQt5 and PySide2.

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
        if _can_import("PySide2.QtCore"):
            return "pyside2"
        elif _can_import("PyQt5.QtCore"):
            return "pyqt5"
        return None

    def set_qt_api(self, api):
        self.pytest_qt_api = self._get_qt_api_from_env() or api or self._guess_qt_api()
        if not self.pytest_qt_api:  # pragma: no cover
            errors = "\n".join(
                f"  {module}: {reason}"
                for module, reason in sorted(self._import_errors.items())
            )
            msg = "pytest-qt requires either PySide2 or PyQt5 installed.\n" + errors
            raise RuntimeError(msg)

        _root_modules = {
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

        # qInfo is not exposed in PySide2 (#232)
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

        # Qt4 and Qt5 have different functions to install a message handler;
        # the plugin will try to use the one that is not None
        self.qInstallMsgHandler = None
        self.qInstallMessageHandler = None

        if self.pytest_qt_api == "pyside2":
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

            def extract_from_variant(variant):
                """PySide2 does not expose QVariant API"""
                return variant

            def make_variant(value=None):
                """PySide2 does not expose QVariant API"""
                return value

            self.extract_from_variant = extract_from_variant
            self.make_variant = make_variant

        elif self.pytest_qt_api == "pyqt5":
            self.Signal = QtCore.pyqtSignal
            self.Slot = QtCore.pyqtSlot
            self.Property = QtCore.pyqtProperty

            if self.pytest_qt_api == "pyqt5":
                _QtWidgets = _import_module("QtWidgets")
                self.QApplication = _QtWidgets.QApplication
                self.QWidget = _QtWidgets.QWidget
                self.qInstallMessageHandler = QtCore.qInstallMessageHandler

                self.QStringListModel = QtCore.QStringListModel
                self.QSortFilterProxyModel = QtCore.QSortFilterProxyModel

                def extract_from_variant(variant):
                    """not needed in PyQt5: Qt API always returns pure python objects"""
                    return variant

                def make_variant(value=None):
                    """Return a QVariant object from the given Python builtin"""
                    return QtCore.QVariant(value)

            else:
                self.QApplication = QtGui.QApplication
                self.QWidget = QtGui.QWidget
                self.qInstallMsgHandler = QtCore.qInstallMsgHandler

                self.QStringListModel = QtGui.QStringListModel
                self.QSortFilterProxyModel = QtGui.QSortFilterProxyModel

                def extract_from_variant(variant):
                    """returns python object from the given QVariant"""
                    if isinstance(variant, QtCore.QVariant):
                        return variant.toPyObject()
                    return variant

                def make_variant(value=None):
                    """Return a QVariant object from the given Python builtin"""
                    return value

            self.QStandardItem = QtGui.QStandardItem
            self.QStandardItemModel = QtGui.QStandardItemModel
            self.QAbstractListModel = QtCore.QAbstractListModel
            self.QAbstractTableModel = QtCore.QAbstractTableModel

            self.extract_from_variant = extract_from_variant
            self.make_variant = make_variant

    def get_versions(self):
        if self.pytest_qt_api == "pyside2":
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
