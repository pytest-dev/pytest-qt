'''
Initial sources from https://github.com/epage/PythonUtils.

Modified to support other modules besides QtCore.
'''

from __future__ import with_statement
from __future__ import division
import os

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:
    try:
        import PySide.QtCore as _QtCore
        QtCore = _QtCore
        USE_PYSIDE = True
    except ImportError:
        USE_PYSIDE = False

    FORCE_PYQT = os.environ.get('PYTEST_QT_FORCE_PYQT', 'false') == 'true'
    if not USE_PYSIDE or FORCE_PYQT:
        try:
            import sip
        except ImportError:
            msg = 'pytest-qt requires either PyQt4 or PySide to be installed'
            raise ImportError(msg)
        USE_PYSIDE = False
        sip.setapi('QString', 2)
        sip.setapi('QVariant', 2)
        import PyQt4.QtCore as _QtCore
        QtCore = _QtCore

    if USE_PYSIDE:
        def _import_module(moduleName):
            pyside = __import__('PySide', globals(), locals(), [moduleName], 0)
            return getattr(pyside, moduleName)
    
        Signal = QtCore.Signal
        Slot = QtCore.Slot
        Property = QtCore.Property
    else:
        def _import_module(moduleName):
            pyside = __import__('PyQt4', globals(), locals(), [moduleName], 0)
            return getattr(pyside, moduleName)
    
        Signal = QtCore.pyqtSignal
        Slot = QtCore.pyqtSlot
        Property = QtCore.pyqtProperty
    
    
    QtGui = _import_module('QtGui')
    QtTest = _import_module('QtTest')
    Qt = QtCore.Qt
    QEvent = QtCore.QEvent
    
else:
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
            elif name[0] == name[0].upper():
                mockType = type(name, (), {})
                mockType.__module__ = __name__
                return mockType
            else:
                return Mock()
    
    QtGui = Mock()
    QtCore = Mock()
    QtTest = Mock()
    Qt = Mock()
    QEvent = Mock()
