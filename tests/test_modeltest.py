import pytest

from pytestqt.qt_compat import QStandardItemModel, QStandardItem, \
    QFileSystemModel, QStringListModel, QSortFilterProxyModel, QT_API, \
    QAbstractListModel, QtCore

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

        def data(self, index=QtCore.QModelIndex(),
                 role=QtCore.Qt.DisplayRole):
            if role == QtCore.Qt.TextAlignmentRole:
                return role_value
            elif role == QtCore.Qt.DisplayRole:
                if index == self.index(0, 0):
                    return 'Hello'
            return None

    check_model(MyModel(), should_pass=should_pass)


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
