import pytest
from pytestqt.qt_compat import QStandardItemModel, QStandardItem, \
    QFileSystemModel, QStringListModel, QSortFilterProxyModel, QT_API

pytestmark = pytest.mark.usefixtures('qtbot')


def test_standard_item_model(qtmodeltester):
    """
    Basic test which uses qtmodeltester with a QStandardItemModel.
    """
    model = QStandardItemModel()
    items = [QStandardItem(str(i)) for i in range(5)]
    items[0].setChild(0, items[4])
    model.setItem(0, 0, items[0])
    model.setItem(0, 1, items[1])
    model.setItem(1, 0, items[2])
    model.setItem(1, 1, items[3])

    qtmodeltester.check(model)


def test_file_system_model(qtmodeltester, tmpdir):
    tmpdir.ensure('directory', dir=1)
    tmpdir.ensure('file1.txt')
    tmpdir.ensure('file2.py')
    model = QFileSystemModel()
    model.setRootPath(str(tmpdir))
    qtmodeltester.check(model)
    tmpdir.ensure('file3.py')
    qtmodeltester.check(model)


@pytest.mark.skipif(QT_API == 'pyside', reason='For some reason this fails in '
                                               'PySide with a message about'
                                               'columnCount being private')
def test_string_list_model(qtmodeltester):
    model = QStringListModel()
    model.setStringList(['hello', 'world'])
    qtmodeltester.check(model)


def test_sort_filter_proxy_model(qtmodeltester):
    model = QStringListModel()
    model.setStringList(['hello', 'world'])
    proxy = QSortFilterProxyModel()
    proxy.setSourceModel(model)
    qtmodeltester.check(proxy)

