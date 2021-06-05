"""
Provide a common way to import Qt classes used by pytest-qt in a unique manner,
abstracting API differences between PyQt5 and PySide2/6.

.. note:: This module is not part of pytest-qt public API, hence its interface
may change between releases and users should not rely on it.

Based on from https://github.com/epage/PythonUtils.
"""


from collections import namedtuple
import os

import pytest


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
        supported_apis = [
            "pyside6",
            "pyside2",
            "pyqt6",
            "pyqt5",
        ]

        if api is not None:
            api = api.lower()
            if api not in supported_apis:  # pragma: no cover
                msg = f"Invalid value for $PYTEST_QT_API: {api}, expected one of {supported_apis}"
                raise pytest.UsageError(msg)
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
        elif _can_import("PyQt6.QtCore"):
            return "pyqt6"
        elif _can_import("PyQt5.QtCore"):
            return "pyqt5"
        return None

    def set_qt_api(self, api):
        self.pytest_qt_api = self._get_qt_api_from_env() or api or self._guess_qt_api()

        self.is_pyside = self.pytest_qt_api in ["pyside2", "pyside6"]
        self.is_pyqt = self.pytest_qt_api in ["pyqt5", "pyqt6"]

        if not self.pytest_qt_api:  # pragma: no cover
            errors = "\n".join(
                f"  {module}: {reason}"
                for module, reason in sorted(self._import_errors.items())
            )
            msg = (
                "pytest-qt requires either PySide2, PySide6, PyQt5 or PyQt6 installed.\n"
                + errors
            )
            raise pytest.UsageError(msg)

        _root_modules = {
            "pyside6": "PySide6",
            "pyside2": "PySide2",
            "pyqt6": "PyQt6",
            "pyqt5": "PyQt5",
        }
        _root_module = _root_modules[self.pytest_qt_api]

        def _import_module(module_name):
            m = __import__(_root_module, globals(), locals(), [module_name], 0)
            return getattr(m, module_name)

        self.QtCore = QtCore = _import_module("QtCore")
        self.QtGui = _import_module("QtGui")
        self.QtTest = _import_module("QtTest")
        self.QtWidgets = _import_module("QtWidgets")

        self._check_qt_api_version()

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

        if self.is_pyside:
            self.Signal = QtCore.Signal
            self.Slot = QtCore.Slot
            self.Property = QtCore.Property
        elif self.is_pyqt:
            self.Signal = QtCore.pyqtSignal
            self.Slot = QtCore.pyqtSlot
            self.Property = QtCore.pyqtProperty
        else:
            assert False, "Expected either is_pyqt or is_pyside"

        if self.pytest_qt_api == "pyside2":
            import shiboken2

            self.isdeleted = lambda obj: not shiboken2.isValid(obj)
        elif self.pytest_qt_api == "pyside6":
            import shiboken6

            self.isdeleted = lambda obj: not shiboken6.isValid(obj)
        else:
            assert self.is_pyqt
            try:
                sip = _import_module("sip")
            except AttributeError:
                # some distributions still package PyQt5.sip as sip (#396)
                import sip
            self.isdeleted = sip.isdeleted

    def _check_qt_api_version(self):
        if not self.is_pyqt:
            # We support all PySide versions
            return

        if self.QtCore.PYQT_VERSION == 0x060000:  # 6.0.0
            raise pytest.UsageError(
                "PyQt 6.0 is not supported by pytest-qt, use 6.1+ instead."
            )
        elif self.QtCore.PYQT_VERSION < 0x050B00:  # 5.11.0
            raise pytest.UsageError(
                "PyQt < 5.11 is not supported by pytest-qt, use 5.11+ instead."
            )

    def exec(self, obj, *args, **kwargs):
        # exec was a keyword in Python 2, so PySide2 (and also PySide6 6.0)
        # name the corresponding method "exec_" instead.
        #
        # The old _exec() alias is removed in PyQt6 and also deprecated as of
        # PySide 6.1:
        # https://codereview.qt-project.org/c/pyside/pyside-setup/+/342095
        if hasattr(obj, "exec"):
            return obj.exec(*args, **kwargs)
        return obj.exec_(*args, **kwargs)

    def get_versions(self):
        if self.pytest_qt_api == "pyside6":
            import PySide6

            version = PySide6.__version__

            return VersionTuple(
                "PySide6", version, self.QtCore.qVersion(), self.QtCore.__version__
            )
        elif self.pytest_qt_api == "pyside2":
            import PySide2

            version = PySide2.__version__

            return VersionTuple(
                "PySide2", version, self.QtCore.qVersion(), self.QtCore.__version__
            )
        elif self.pytest_qt_api == "pyqt6":
            return VersionTuple(
                "PyQt6",
                self.QtCore.PYQT_VERSION_STR,
                self.QtCore.qVersion(),
                self.QtCore.QT_VERSION_STR,
            )
        elif self.pytest_qt_api == "pyqt5":
            return VersionTuple(
                "PyQt5",
                self.QtCore.PYQT_VERSION_STR,
                self.QtCore.qVersion(),
                self.QtCore.QT_VERSION_STR,
            )

        assert False, f"Internal error, unknown pytest_qt_api: {self.pytest_qt_api}"


qt_api = _QtApi()
