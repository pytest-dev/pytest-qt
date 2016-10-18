"""
Provide a common way to import Qt classes used by pytest-qt in a unique manner,
abstracting API differences between PyQt4, PyQt5 and PySide.

.. note:: This module is not part of pytest-qt public API, hence its interface
may change between releases and users should not rely on it.

Based on from https://github.com/epage/PythonUtils.
"""

from __future__ import with_statement
from __future__ import division
from collections import namedtuple
import os


VersionTuple = namedtuple('VersionTuple', 'qt_api, qt_api_version, runtime, compiled')


class _QtApi:
    """
    Interface to the underlying Qt API currently configured for pytest-qt.

    This object lazily loads all class references and other objects when the ``set_qt_api`` method
    gets called, providing a uniform way to access the Qt classes.
    """

    def _get_qt_api_from_env(self):
        api = os.environ.get('PYTEST_QT_API')
        if api is not None:
            api = api.lower()
            if api not in ('pyside', 'pyqt4', 'pyqt4v2', 'pyqt5'):  # pragma: no cover
                msg = 'Invalid value for $PYTEST_QT_API: %s'
                raise RuntimeError(msg % qt_api)
        return api

    def _guess_qt_api(self):  # pragma: no cover
        def _can_import(name):
            try:
                __import__(name)
                return True
            except ImportError:
                return False

        if _can_import('PyQt5'):
            return 'pyqt5'
        elif _can_import('PySide'):
            return 'pyside'
        elif _can_import('PyQt4'):
            return 'pyqt4'
        return None

    def set_qt_api(self, api):
        self.pytest_qt_api = api or self._get_qt_api_from_env() or self._guess_qt_api()
        if not self.pytest_qt_api:  # pragma: no cover
            msg = 'pytest-qt requires either PySide, PyQt4 or PyQt5 to be installed'
            raise RuntimeError(msg)

        _root_modules = {
            'pyside': 'PySide',
            'pyqt4': 'PyQt4',
            'pyqt4v2': 'PyQt4',
            'pyqt5': 'PyQt5',
        }
        _root_module = _root_modules[self.pytest_qt_api]

        def _import_module(module_name):
            m = __import__(_root_module, globals(), locals(), [module_name], 0)
            return getattr(m, module_name)

        if self.pytest_qt_api == 'pyqt4v2':  # pragma: no cover
            # the v2 api in PyQt4
            # http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html
            import sip
            sip.setapi("QDate", 2)
            sip.setapi("QDateTime", 2)
            sip.setapi("QString", 2)
            sip.setapi("QTextStream", 2)
            sip.setapi("QTime", 2)
            sip.setapi("QUrl", 2)
            sip.setapi("QVariant", 2)

        self.QtCore = QtCore = _import_module('QtCore')
        self.QtGui = QtGui = _import_module('QtGui')
        self.QtTest = _import_module('QtTest')
        self.Qt = QtCore.Qt
        self.QEvent = QtCore.QEvent

        self.qDebug = QtCore.qDebug
        self.qWarning = QtCore.qWarning
        self.qCritical = QtCore.qCritical
        self.qFatal = QtCore.qFatal
        self.QtDebugMsg = QtCore.QtDebugMsg
        self.QtWarningMsg = QtCore.QtWarningMsg
        self.QtCriticalMsg = QtCore.QtCriticalMsg
        self.QtFatalMsg = QtCore.QtFatalMsg

        # Qt4 and Qt5 have different functions to install a message handler;
        # the plugin will try to use the one that is not None
        self.qInstallMsgHandler = None
        self.qInstallMessageHandler = None

        if self.pytest_qt_api == 'pyside':
            self.Signal = QtCore.Signal
            self.Slot = QtCore.Slot
            self.Property = QtCore.Property
            self.QApplication = QtGui.QApplication
            self.QWidget = QtGui.QWidget
            self.QLineEdit = QtGui.QLineEdit
            self.QStringListModel = QtGui.QStringListModel
            self.qInstallMsgHandler = QtCore.qInstallMsgHandler

            self.QStandardItem = QtGui.QStandardItem
            self.QStandardItemModel = QtGui.QStandardItemModel
            self.QStringListModel = QtGui.QStringListModel
            self.QSortFilterProxyModel = QtGui.QSortFilterProxyModel
            self.QAbstractListModel = QtCore.QAbstractListModel
            self.QAbstractTableModel = QtCore.QAbstractTableModel

            def extract_from_variant(variant):
                """PySide does not expose QVariant API"""
                return variant

            def make_variant(value=None):
                """PySide does not expose QVariant API"""
                return value

            self.extract_from_variant = extract_from_variant
            self.make_variant = make_variant

        elif self.pytest_qt_api in ('pyqt4', 'pyqt4v2', 'pyqt5'):
            self.Signal = QtCore.pyqtSignal
            self.Slot = QtCore.pyqtSlot
            self.Property = QtCore.pyqtProperty

            if self.pytest_qt_api == 'pyqt5':
                _QtWidgets = _import_module('QtWidgets')
                self.QApplication = _QtWidgets.QApplication
                self.QWidget = _QtWidgets.QWidget
                self.QLineEdit = _QtWidgets.QLineEdit
                self.qInstallMessageHandler = QtCore.qInstallMessageHandler

                self.QStringListModel = QtCore.QStringListModel
                self.QSortFilterProxyModel = QtCore.QSortFilterProxyModel

                def extract_from_variant(variant):
                    """not needed in PyQt5: Qt API always returns pure python objects"""
                    return variant

                def make_variant(value=None):
                    """Return a QVariant object from the given Python builtin"""
                    # PyQt4 doesn't allow one to instantiate any QVariant at all:
                    # QVariant represents a mapped type and cannot be instantiated
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
                    # PyQt4 doesn't allow one to instantiate any QVariant at all:
                    # QVariant represents a mapped type and cannot be instantiated
                    return value

            self.QStandardItem = QtGui.QStandardItem
            self.QStandardItemModel = QtGui.QStandardItemModel
            self.QAbstractListModel = QtCore.QAbstractListModel
            self.QAbstractTableModel = QtCore.QAbstractTableModel

            self.extract_from_variant = extract_from_variant
            self.make_variant = make_variant

    def get_versions(self):
        if self.pytest_qt_api == 'pyside':
            import PySide
            return VersionTuple('PySide', PySide.__version__, self.QtCore.qVersion(),
                                self.QtCore.__version__)
        else:
            qt_api_name = 'PyQt5' if self.pytest_qt_api == 'pyqt5' else 'PyQt4'
            return VersionTuple(qt_api_name, self.QtCore.PYQT_VERSION_STR,
                                self.QtCore.qVersion(), self.QtCore.QT_VERSION_STR)

qt_api = _QtApi()
