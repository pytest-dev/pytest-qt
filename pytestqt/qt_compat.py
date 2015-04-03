'''
Initial sources from https://github.com/epage/PythonUtils.

Modified to support other modules besides QtCore.
'''

from __future__ import with_statement
from __future__ import division
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
            raise ImportError(msg)

    # backward compatibility support: PYTEST_QT_FORCE_PYQT
    if os.environ.get('PYTEST_QT_FORCE_PYQT', 'false') == 'true':
        QT_API = 'pyqt4'
    else:
        QT_API = os.environ.get('PYTEST_QT_API')
        if QT_API is not None:
            QT_API = QT_API.lower()
            if QT_API not in ('pyside', 'pyqt4', 'pyqt5'):
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
        'pyqt5': 'PyQt5',
    }
    _root_module = _root_modules[QT_API]

    QtCore = _import_module('QtCore')
    QtGui = _import_module('QtGui')
    QtTest = _import_module('QtTest')
    Qt = QtCore.Qt
    QEvent = QtCore.QEvent

    if QT_API == 'pyside':
        Signal = QtCore.Signal
        Slot = QtCore.Slot
        Property = QtCore.Property
        QApplication = QtGui.QApplication
        QWidget = QtGui.QWidget

    elif QT_API in ('pyqt4', 'pyqt5'):
        Signal = QtCore.pyqtSignal
        Slot = QtCore.pyqtSlot
        Property = QtCore.pyqtProperty

        if QT_API == 'pyqt5':
            _QtWidgets = _import_module('QtWidgets')
            QApplication = _QtWidgets.QApplication
            QWidget = _QtWidgets.QWidget
        else:
            QApplication = QtGui.QApplication
            QWidget = QtGui.QWidget

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
            elif name == '__name__':
                return name
            else:
                return Mock()
    
    QtGui = Mock()
    QtCore = Mock()
    QtTest = Mock()
    Qt = Mock()
    QEvent = Mock()
    QApplication = Mock()
    QWidget = Mock()
    QT_API = '<none>'
