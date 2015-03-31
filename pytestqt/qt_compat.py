'''
Initial sources from https://github.com/epage/PythonUtils.

Modified to support other modules besides QtCore.
'''

from __future__ import with_statement
from __future__ import division
import os

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # pragma: no cover
    try:
        from PySide import QtCore
        USING_PYSIDE = True
    except ImportError:
        USING_PYSIDE = False

    FORCE_PYQT = os.environ.get('PYTEST_QT_FORCE_PYQT', 'false') != 'false'
    PYQT_VER = None
    if not USING_PYSIDE or FORCE_PYQT:
        try:
            import sip
        except ImportError:
            msg = 'pytest-qt requires either PyQt4 or PySide to be installed'
            raise ImportError(msg)

        if 'PYTEST_QT_FORCE_PYQT' in os.environ:
            PYQT_VER = os.environ.get('PYTEST_QT_FORCE_PYQT', '4')
            # backward compatibility
            if PYQT_VER == 'true':
                PYQT_VER = '4'
            if PYQT_VER not in ('4', '5'):
                msg = 'Unsupported PyQt version in $PYTEST_QT_FORCE_PYQT: %s'
                raise RuntimeError(msg % PYQT_VER)
        else:
            # give preference for PyQt4 for backward compatibility
            try:
                import PyQt4
                PYQT_VER = '4'
            except ImportError:
                import PyQt5
                PYQT_VER = '5'

        USING_PYSIDE = False

    if USING_PYSIDE:
        def _import_module(module_name):
            pyside = __import__('PySide', globals(), locals(), [module_name], 0)
            return getattr(pyside, module_name)
    
        Signal = QtCore.Signal
        Slot = QtCore.Slot
        Property = QtCore.Property
    else:
        def _import_module(module_name):
            pyside = __import__('PyQt%s' % PYQT_VER,
                                globals(), locals(), [module_name], 0)
            return getattr(pyside, module_name)

        QtCore = _import_module('QtCore')
        Signal = QtCore.pyqtSignal
        Slot = QtCore.pyqtSlot
        Property = QtCore.pyqtProperty
    
    
    QtGui = _import_module('QtGui')
    QtTest = _import_module('QtTest')
    Qt = QtCore.Qt
    QEvent = QtCore.QEvent
    if not USING_PYSIDE and PYQT_VER == '5':
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
