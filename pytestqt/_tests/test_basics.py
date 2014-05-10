from pytestqt.qt_compat import QtGui, Qt, QEvent
import pytest


#===================================================================================================
# fixtures
#===================================================================================================
@pytest.fixture
def event_recorder(qtbot):
    widget = EventRecorder()
    qtbot.addWidget(widget)
    return widget


#===================================================================================================
# testBasics
#===================================================================================================
def testBasics(qtbot):
    '''
    Basic test that works more like a sanity check to ensure we are setting up a QApplication
    properly and are able to display a simple event_recorder. 
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
def testKeyEvents(qtbot, event_recorder):
    '''
    Basic key events test.
    '''
    def extract(key_event):
        return (
            key_event.type(),
            key_event.key(),
            key_event.text(),
        )
        
    event_recorder.registerEvent(QtGui.QKeyEvent, extract)
    
    qtbot.keyPress(event_recorder, 'a')
    assert event_recorder.event_data == (QEvent.KeyPress, int(Qt.Key_A), 'a')
    
    qtbot.keyRelease(event_recorder, 'a')
    assert event_recorder.event_data == (QEvent.KeyRelease, int(Qt.Key_A), 'a')
    
    
#===================================================================================================
# testMouseEvents
#===================================================================================================
def testMouseEvents(qtbot, event_recorder):
    '''
    Basic mouse events test.
    '''
    def extract(mouse_event):
        return (
            mouse_event.type(),
            mouse_event.button(),
            mouse_event.modifiers(),
        )
        
    event_recorder.registerEvent(QtGui.QMouseEvent, extract)
    
    qtbot.mousePress(event_recorder, Qt.LeftButton)
    assert event_recorder.event_data == (QEvent.MouseButtonPress, Qt.LeftButton, Qt.NoModifier)
    
    qtbot.mousePress(event_recorder, Qt.RightButton, Qt.AltModifier)
    assert event_recorder.event_data == (QEvent.MouseButtonPress, Qt.RightButton, Qt.AltModifier)
    
    
#===================================================================================================
# EventRecorder
#===================================================================================================
class EventRecorder(QtGui.QWidget):
    '''
    Widget that records some kind of events sent to it.
    
    When this event_recorder receives a registered event (by calling `registerEvent`), it will call
    the associated *extract* function and hold the return value from the function in the 
    `event_data` member.
    '''
        
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self._event_types = {}
        self.event_data = None
        
        
    def registerEvent(self, event_type, extract_func):
        self._event_types[event_type] = extract_func
        
    
    def event(self, ev):
        for event_type, extract_func in self._event_types.items():
            if type(ev) is event_type:
                self.event_data = extract_func(ev)
                return True
        
        return False
    
    
#===================================================================================================
# main
#===================================================================================================
if __name__ == '__main__':
    pytest.main(args=['-s'])