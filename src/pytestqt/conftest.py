import pytest
from pytestqt.qt_compat import QtGui 

#===================================================================================================
# QtBot
#===================================================================================================
class QtBot(object):
    '''
    Responsible for sending events to Qt objects, simulating user input.
    
    Instances of this class should be accessed by the ``qtbot`` pytest fixture.
    '''
    
    def __init__(self, app):
        '''
        :param QApplication app: 
            The current QApplication instance.
        '''
        self._app = app
        self._widgets = []
        
        
    def _close(self):
        '''
        Clear up method. Called at the end of each test that uses a qtbot fixture.
        '''
        for w in self._widgets:
            w.close()
        self._widgets[:] = []
        
        
    def addWidget(self, widget):
        '''
        Adds a widget to be tracked by this bot. This is not required, but will ensure that the
        widget gets closed by the end of the test, so it is highly recommended.
        
        :param QWidget widget: 
            Widget to keep track of.
        '''
        self._widgets.append(widget)


#===================================================================================================
# pytest_configure
#===================================================================================================
def pytest_configure(config):
    '''
    PyTest plugin API. Called before the start of each test session.
    
    :param config.Config config:  
    '''
    qt_app_instance = QtGui.QApplication([])
    config.qt_app_instance = qt_app_instance
    
    def exit_qapp():
        '''
        Makes sure to exit the application after all tests finish running.
        '''
        qt_app_instance.exit()
        
    config._cleanup.append(exit_qapp)


#===================================================================================================
# qtbot
#===================================================================================================
@pytest.fixture
def qtbot(request):
    '''
    Fixture used to create a QtBot instance for using during testing. 
    
    Make sure to call addWidget for each top-level widget you create to ensure that they are
    properly closed after the test ends.
    '''
    result = QtBot(request.config.qt_app_instance)
    request.addfinalizer(result._close)
    return result

