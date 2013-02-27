import pytest
from _pytest.python import FixtureRequest

#===================================================================================================
# QtHandler
#===================================================================================================
class QtHandler(object):
    
    def __init__(self, app):
        print 'QtHandler()'
        self._app = app
        self._widgets = []
        
        
    def _close(self):
        print 'QtHandler._close()(%d widgets)' % len(self._widgets)
        for w in self._widgets:
            w.close()
        self._widgets[:] = []
        
        
    def addWidget(self, widget):
        self._widgets.append(widget)
