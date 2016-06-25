import os

import pytest

from pytestqt.qt_compat import QStandardItemModel, QStandardItem, \
    QFileSystemModel, QStringListModel, QSortFilterProxyModel, QT_API, \
    QAbstractListModel, QtCore

pytestmark = pytest.mark.usefixtures('qtbot')


class BasicModel(QtCore.QAbstractItemModel):

    def data(self, index, role=QtCore.Qt.DisplayRole):
        return None

    def rowCount(self, parent=QtCore.QModelIndex()):
        return 0

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 0

    def index(self, row, column, parent=QtCore.QModelIndex()):
        return QtCore.QModelIndex()

    def parent(self, index):
        return QtCore.QModelIndex()


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


@pytest.mark.parametrize('broken_role', [
    QtCore.Qt.ToolTipRole, QtCore.Qt.StatusTipRole,
    QtCore.Qt.WhatsThisRole,
    QtCore.Qt.SizeHintRole, QtCore.Qt.FontRole,
    QtCore.Qt.BackgroundColorRole,
    QtCore.Qt.TextColorRole, QtCore.Qt.TextAlignmentRole,
    QtCore.Qt.CheckStateRole,
])
def test_broken_types(check_model, broken_role):
    """
    Check that qtmodeltester correctly captures data() returning invalid
    values for various display roles.
    """
    class BrokenTypeModel(QAbstractListModel):

        def rowCount(self, parent=QtCore.QModelIndex()):
            if parent == QtCore.QModelIndex():
                return 1
            else:
                return 0

        def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
            if role == broken_role:
                return object()  # This will fail the type check for any role
            else:
                return None

    check_model(BrokenTypeModel(), should_pass=False)


@pytest.mark.parametrize('role_value, should_pass', [
    (QtCore.Qt.AlignLeft, True),
    (QtCore.Qt.AlignRight, True),
    (0xFFFFFF, False),
])
def test_data_alignment(role_value, should_pass, check_model):
    """Test a custom model which returns a good and alignments from data().
    qtmodeltest should capture this problem and fail when that happens.
    """
    class MyModel(QAbstractListModel):

        def rowCount(self, parent=QtCore.QModelIndex()):
            return 1 if parent == QtCore.QModelIndex() else 0

        def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
            if role == QtCore.Qt.TextAlignmentRole:
                return role_value
            elif role == QtCore.Qt.DisplayRole:
                if index == self.index(0, 0):
                    return 'Hello'
            return None

    check_model(MyModel(), should_pass=should_pass)


def test_header_handling(check_model):

    class MyModel(QAbstractListModel):

        def rowCount(self, parent=QtCore.QModelIndex()):
            return 1 if parent == QtCore.QModelIndex() else 0

        def set_header_text(self, header):
            self._header_text = header
            self.headerDataChanged.emit(QtCore.Qt.Vertical, 0, 0)
            self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, 0)

        def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
            return self._header_text

        def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
            if role == QtCore.Qt.DisplayRole and index == self.index(0, 0):
                return 'Contents'
            return None

    model = MyModel()
    model.set_header_text('Start Header')
    check_model(model, should_pass=1)
    model.set_header_text('New Header')


@pytest.fixture
def check_model(qtmodeltester):
    """
    Return a check_model(model, should_pass=True) function that uses
    qtmodeltester to check if the model is OK or not according to the
    ``should_pass`` parameter.
    """
    def check(model, should_pass=True):
        if should_pass:
            qtmodeltester.check(model)
        else:
            with pytest.raises(AssertionError):
                qtmodeltester.check(model)
    return check


def test_invalid_column_count(qtmodeltester):
    """Basic check with an invalid model."""
    class Model(BasicModel):
        def columnCount(self, parent=QtCore.QModelIndex()):
            return -1

    model = Model()

    with pytest.raises(AssertionError):
        qtmodeltester.check(model)


def test_changing_model_insert(qtmodeltester):
    model = QStandardItemModel()
    item = QStandardItem('foo')
    qtmodeltester.check(model)
    model.insertRow(0, item)


def test_changing_model_remove(qtmodeltester):
    model = QStandardItemModel()
    item = QStandardItem('foo')
    model.setItem(0, 0, item)
    qtmodeltester.check(model)
    model.removeRow(0)


def test_changing_model_data(qtmodeltester):
    model = QStandardItemModel()
    item = QStandardItem('foo')
    model.setItem(0, 0, item)
    qtmodeltester.check(model)
    model.setData(model.index(0, 0), 'hello world')


@pytest.mark.parametrize('orientation', [QtCore.Qt.Horizontal,
                                         QtCore.Qt.Vertical])
def test_changing_model_header_data(qtmodeltester, orientation):
    model = QStandardItemModel()
    item = QStandardItem('foo')
    model.setItem(0, 0, item)
    qtmodeltester.check(model)
    model.setHeaderData(0, orientation, 'blah')


def test_changing_model_sort(qtmodeltester):
    """Sorting emits layoutChanged"""
    model = QStandardItemModel()
    item = QStandardItem('foo')
    model.setItem(0, 0, item)
    qtmodeltester.check(model)
    model.sort(0)


def test_nop(qtmodeltester):
    """We should not get a crash on cleanup with no model."""
    pass


def test_fetch_more(qtmodeltester):
    class Model(BasicModel):

        def rowCount(self, parent=None):
            if parent is None:
                1/0
                return 1
            else:
                return 0

        def canFetchMore(self, parent):
            return True

        def fetchMore(self, parent):
            pass

    model = Model()
    qtmodeltester.check(model)
