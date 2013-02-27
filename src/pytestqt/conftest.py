import pytest
from pytestqt.qt_compat import QtGui 
from pytestqt import QtHandler


#===================================================================================================
# pytest_configure
#===================================================================================================
def pytest_configure(config):
    qt_app_instance = QtGui.QApplication([])
    print 'Create:qApp:%s' % qt_app_instance
    config.qt_app_instance = qt_app_instance
    def exit():
        qt_app_instance.exit()
        print 'Close:qApp:%s' % qt_app_instance
    config._cleanup.append(exit)

#===================================================================================================
# qt
#===================================================================================================
@pytest.fixture
def qt(request):
    print 'NodeName:', repr(request.node.name)
    result = QtHandler(request.config.qt_app_instance)
    request.addfinalizer(result._close)
    return result

