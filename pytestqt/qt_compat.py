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

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # pragma: no cover

    def _try_import(name):
        try:
            __import__(name)
            return True
        except ImportError:
            return False

    def _guess_qt_api():
        if _try_import('PySide'):
            return 'pyside'
        elif _try_import('PyQt4'):
            return 'pyqt4'
        elif _try_import('PyQt5'):
            return 'pyqt5'
        else:
            msg = 'pytest-qt requires either PySide, PyQt4 or PyQt5 to be installed'
            raise RuntimeError(msg)

    # backward compatibility support: PYTEST_QT_FORCE_PYQT
    if os.environ.get('PYTEST_QT_FORCE_PYQT', 'false') == 'true':
        QT_API = 'pyqt4'
    else:
        QT_API = os.environ.get('PYTEST_QT_API')
        if QT_API is not None:
            QT_API = QT_API.lower()
            if QT_API not in ('pyside', 'pyqt4', 'pyqt4v2', 'pyqt5'):
                msg = 'Invalid value for $PYTEST_QT_API: %s'
                raise RuntimeError(msg % QT_API)
        else:
            QT_API = _guess_qt_api()

    # backward compatibility
    USING_PYSIDE = QT_API == 'pyside'

    def _import_module(module_name):
        m = __import__(_root_module, globals(), locals(), [module_name], 0)
        return getattr(m, module_name)

    _root_modules = {
        'pyside': 'PySide',
        'pyqt4': 'PyQt4',
        'pyqt4v2': 'PyQt4',
        'pyqt5': 'PyQt5',
    }
    _root_module = _root_modules[QT_API]

    if QT_API == 'pyqt4v2':
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

    QtCore = _import_module('QtCore')
    QtGui = _import_module('QtGui')
    QtTest = _import_module('QtTest')
    Qt = QtCore.Qt
    QEvent = QtCore.QEvent

    qDebug = QtCore.qDebug
    qWarning = QtCore.qWarning
    qCritical = QtCore.qCritical
    qFatal = QtCore.qFatal
    QtDebugMsg = QtCore.QtDebugMsg
    QtWarningMsg = QtCore.QtWarningMsg
    QtCriticalMsg = QtCore.QtCriticalMsg
    QtFatalMsg = QtCore.QtFatalMsg

    # Qt4 and Qt5 have different functions to install a message handler;
    # the plugin will try to use the one that is not None
    qInstallMsgHandler = None
    qInstallMessageHandler = None

    VersionTuple = namedtuple('VersionTuple',
                              'qt_api, qt_api_version, runtime, compiled')

    if QT_API == 'pyside':
        import PySide
        Signal = QtCore.Signal
        Slot = QtCore.Slot
        Property = QtCore.Property
        QApplication = QtGui.QApplication
        QWidget = QtGui.QWidget
        qInstallMsgHandler = QtCore.qInstallMsgHandler

        def get_versions():
            return VersionTuple('PySide', PySide.__version__, QtCore.qVersion(),
                                QtCore.__version__)

    elif QT_API in ('pyqt4', 'pyqt4v2', 'pyqt5'):
        Signal = QtCore.pyqtSignal
        Slot = QtCore.pyqtSlot
        Property = QtCore.pyqtProperty

        if QT_API == 'pyqt5':
            _QtWidgets = _import_module('QtWidgets')
            QApplication = _QtWidgets.QApplication
            QWidget = _QtWidgets.QWidget
            qInstallMessageHandler = QtCore.qInstallMessageHandler
            qt_api_name = 'PyQt5'
        else:
            QApplication = QtGui.QApplication
            QWidget = QtGui.QWidget
            qInstallMsgHandler = QtCore.qInstallMsgHandler
            qt_api_name = 'PyQt4'

        def get_versions():
            return VersionTuple(qt_api_name, QtCore.PYQT_VERSION_STR,
                                QtCore.qVersion(), QtCore.QT_VERSION_STR)

else:  # pragma: no cover
    USING_PYSIDE = True

    # mock Qt when we are generating documentation at readthedocs.org
    class Mock(object):
        def __init__(self, *args, **kwargs):
            pass
    
        def __call__(self, *args, **kwargs):
            return Mock()
    
        @classmethod
        def __getattr__(cls, name):
            if name in ('__file__', '__path__'):
                return '/dev/null'
            elif name in ('__name__', '__qualname__'):
                return name
            elif name == '__annotations__':
                return {}
            else:
                return Mock()
    
    QtGui = Mock()
    QtCore = Mock()
    QtTest = Mock()
    Qt = Mock()
    QEvent = Mock()
    QApplication = Mock()
    QWidget = Mock()
    qInstallMsgHandler = Mock()
    qInstallMessageHandler = Mock()
    qDebug = Mock()
    qWarning = Mock()
    qCritical = Mock()
    qFatal = Mock()
    QtDebugMsg = Mock()
    QtWarningMsg = Mock()
    QtCriticalMsg = Mock()
    QtFatalMsg = Mock()
    QT_API = '<none>'
