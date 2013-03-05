from pytestqt.qt_compat import QtGui 
import pytest


#===================================================================================================
# test_basics
#===================================================================================================
def test_basics(qtbot):
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
# main
#===================================================================================================
if __name__ == '__main__':
    pytest.main(args=['-s'])