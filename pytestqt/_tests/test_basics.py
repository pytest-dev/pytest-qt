from pytestqt.qt_compat import QtGui, Qt, QEvent
import pytest


#===================================================================================================
# testBasics
#===================================================================================================
def testBasics(qtbot):
    '''
    Basic test that works more like a sanity check to ensure we are setting up a QApplication
    properly and are able to display a simple widget. 
    '''
    assert type(QtGui.qApp) is QtGui.QApplication
    widget = QtGui.QWidget()
    qtbot.addWidget(widget)
    widget.setWindowTitle('W1')
    widget.show()
    
    assert widget.isVisible()
    assert widget.windowTitle() == 'W1'
    
    
#===================================================================================================
# testKeyEvents
#===================================================================================================
def testKeyEvents(qtbot):
    '''
    Basic key events test.
    '''
    
    class MyWidget(QtGui.QWidget):
        
        def __init__(self):
            QtGui.QWidget.__init__(self)
            self._reset()
        
        def event(self, ev):
            if type(ev) is QtGui.QKeyEvent:
                self._record(ev)
                return True
            
            return False
        
        
        def _record(self, key_event):
            self.type = key_event.type()
            self.key = key_event.key()
            self.text = key_event.text()
            self.modifiers = key_event.modifiers()
            
            
        def _reset(self):
            self.type = None
            self.key = None
            self.text = None
            self.modifiers = None
            
            
        def assertEvent(self, event_type, key, text, modifiers=Qt.NoModifier):
            assert self.type == event_type
            assert self.key == key
            assert self.text == text
            assert self.modifiers == modifiers
            self._reset()
        
    
    # create test widget
    widget = MyWidget()
    qtbot.addWidget(widget)
    
    qtbot.keyPress(widget, 'a')
    widget.assertEvent(QEvent.KeyPress, int(Qt.Key_A), 'a')
    
    qtbot.keyRelease(widget, 'a')
    widget.assertEvent(QEvent.KeyRelease, int(Qt.Key_A), 'a')
    
    
#===================================================================================================
# main
#===================================================================================================
if __name__ == '__main__':
    pytest.main(args=['-s'])