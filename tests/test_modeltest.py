import pytest
from pytestqt.qt_compat import QStandardItemModel, QStandardItem, \
    QFileSystemModel, QStringListModel, QSortFilterProxyModel, QT_API, QtCore

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


@pytest.mark.parametrize('broken_role', [
    QtCore.Qt.ToolTipRole, QtCore.Qt.StatusTipRole, QtCore.Qt.WhatsThisRole,
    QtCore.Qt.SizeHintRole, QtCore.Qt.FontRole, QtCore.Qt.BackgroundColorRole,
    QtCore.Qt.TextColorRole, QtCore.Qt.TextAlignmentRole,
    QtCore.Qt.CheckStateRole
])
def test_broken_types(testdir, broken_role):
    """
    Check that qtmodeltester correctly captures data() returning invalid
    values for various display roles.
    """
    testdir.makepyfile('''
        from pytestqt.qt_compat import QAbstractListModel, QtCore

        invalid_obj = object()  # This will fail the type check for any role

        class BrokenTypeModel(QAbstractListModel):

            def rowCount(self, parent=QtCore.QModelIndex()):
                if parent == QtCore.QModelIndex():
                    return 1
                else:
                    return 0

            def data(self, index=QtCore.QModelIndex(),
                     role=QtCore.Qt.DisplayRole):
                if role == {broken_role}:
                    return invalid_obj
                else:
                    return None

        def test_broken_type(qtmodeltester):
            model = BrokenTypeModel()
            qtmodeltester.check(model)

        def test_passing():
            # Sanity test to make sure the imports etc. are right
            pass
    '''.format(broken_role=broken_role))
    res = testdir.inline_run()
    res.assertoutcome(passed=1, failed=1)
