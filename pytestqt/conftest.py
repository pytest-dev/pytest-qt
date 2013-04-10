import pytest
from pytestqt.qt_compat import QtGui 
from pytestqt.qt_compat import QtTest

#===================================================================================================
# QtBot
#===================================================================================================
class QtBot(object):
    '''
    Instances of this class are responsible for sending events to `Qt` objects (usually widgets), 
    simulating user input. 
    
    .. important:: Instances of this class should be accessed only by using a ``qtbot`` fixture, 
                    never instantiated directly.
    
    **Widgets**
    
    .. automethod:: addWidget
    .. automethod:: waitForWindowShown
    .. automethod:: stopForInteraction

    **Raw QTest API**
    
    Methods below provide very low level functions, as sending a single mouse click or a key event.
    Thos methods are just forwarded directly to the `QTest API`_. Consult the documentation for more
    information.
    
    ---
    
    Below are methods used to simulate sending key events to widgets:
    
    .. staticmethod:: keyPress(widget, key[, modifier=Qt.NoModifier[, delay=-1]])
    .. staticmethod:: keyClick (widget, key[, modifier=Qt.NoModifier[, delay=-1]])
    .. staticmethod:: keyClicks (widget, key sequence[, modifier=Qt.NoModifier[, delay=-1]])
    .. staticmethod:: keyEvent (action, widget, key[, modifier=Qt.NoModifier[, delay=-1]])
    .. staticmethod:: keyPress (widget, key[, modifier=Qt.NoModifier[, delay=-1]])
    .. staticmethod:: keyRelease (widget, key[, modifier=Qt.NoModifier[, delay=-1]])
    
        Sends one or more keyword events to a widget.
    
        :param QWidget widget: the widget that will receive the event
        
        :param str|int key: key to send, it can be either a Qt.Key_* constant or a single character string.
        
        .. _keyboard modifiers:
        
        :param Qt.KeyboardModifier modifier: flags OR'ed together representing other modifier keys
            also pressed. Possible flags are:
        
            * ``Qt.NoModifier``: No modifier key is pressed.
            * ``Qt.ShiftModifier``: A Shift key on the keyboard is pressed.
            * ``Qt.ControlModifier``: A Ctrl key on the keyboard is pressed.
            * ``Qt.AltModifier``: An Alt key on the keyboard is pressed.
            * ``Qt.MetaModifier``: A Meta key on the keyboard is pressed.
            * ``Qt.KeypadModifier``: A keypad button is pressed.
            * ``Qt.GroupSwitchModifier``: X11 only. A Mode_switch key on the keyboard is pressed.
            
        :param int delay: after the event, delay the test for this miliseconds (if > 0).
        
    
    .. staticmethod:: keyToAscii (key)
        
        Auxilliary method that converts the given constant ot its equivalent ascii.
        
        :param Qt.Key_* key: one of the constants for keys in the Qt namespace.
        
        :return type: str 
        :returns: the equivalent character string. 
    
    ---
    
    Below are methods used to simulate sending mouse events to widgets.
    
    .. staticmethod:: mouseClick (widget, button[, stateKey=0[, pos=QPoint()[, delay=-1]]])
    .. staticmethod:: mouseDClick (widget, button[, stateKey=0[, pos=QPoint()[, delay=-1]]])
    .. staticmethod:: mouseEvent (action, widget, button, stateKey, pos[, delay=-1])
    .. staticmethod:: mouseMove (widget[, pos=QPoint()[, delay=-1]])
    .. staticmethod:: mousePress (widget, button[, stateKey=0[, pos=QPoint()[, delay=-1]]])
    .. staticmethod:: mouseRelease (widget, button[, stateKey=0[, pos=QPoint()[, delay=-1]]])
    
        Sends a mouse moves and clicks to a widget.
        
        :param QWidget widget: the widget that will receive the event
        
        :param Qt.MouseButton button: flags OR'ed together representing the button pressed. 
            Possible flags are:
        
            * ``Qt.NoButton``: The button state does not refer to any button (see QMouseEvent.button()).
            * ``Qt.LeftButton``: The left button is pressed, or an event refers to the left button. (The left button may be the right button on left-handed mice.)
            * ``Qt.RightButton``: The right button.
            * ``Qt.MidButton``: The middle button.
            * ``Qt.MiddleButton``: The middle button.
            * ``Qt.XButton1``: The first X button.
            * ``Qt.XButton2``: The second X button.
            
        :param Qt.KeyboardModifier modifier: flags OR'ed together representing other modifier keys
            also pressed. See `keyboard modifiers`_.
            
        :param QPoint position: position of the mouse pointer.
        
        :param int delay: after the event, delay the test for this miliseconds (if > 0).
            
    
    .. _QTest API: http://doc.qt.digia.com/4.7/qtest.html
    
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
        Clear up method. Called at the end of each test that uses a ``qtbot`` fixture.
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
        
        
    def waitForWindowShown(self, widget):
        '''
        Waits until the window is shown in the screen. This is mainly useful for asynchronous 
        systems like X11, where a window will be mapped to screen some time after being asked to 
        show itself on the screen. 
        
        :param QWidget widget:
            Widget to wait on.
        '''
        QtTest.QTest.qWaitForWindowShown(widget)
        
        
    def stopForInteraction(self):
        '''
        Stops the current test flow, letting the user interact with any visible widget.
        
        This is mainly useful so that you can verify the current state of the program while writing
        tests.
        
        Closing the windows should resume the test run, with ``qtbot`` attempting to restore visibility
        of the widgets as they were before this call.        
        '''
        widget_visibility = [widget.isVisible() for widget in self._widgets]
        
        self._app.exec_()    

        for index, visible in enumerate(widget_visibility):
            widget = self._widgets[index]
            widget.setVisible(visible)


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




#===================================================================================================
# Inject QtTest Functions
#===================================================================================================
def _createQTestProxyMethod(method_name):
    
    def result(*args, **kwargs):
        method = getattr(QtTest.QTest, method_name) 
        return method(*args, **kwargs)
    
    result.__name__ = method_name
    return staticmethod(result)

# inject methods from QTest into QtBot
method_names = set([
    'keyPress',
    'keyClick',
    'keyClicks',
    'keyEvent',
    'keyPress',
    'keyRelease',
    'keyToAscii',
    
    'mouseClick',
    'mouseDClick',
    'mouseEvent',
    'mouseMove',
    'mousePress',
    'mouseRelease',
    
    
])
for method_name in method_names:        
    method = _createQTestProxyMethod(method_name)
    setattr(QtBot, method_name, method)
    