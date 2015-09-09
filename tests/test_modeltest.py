import pytest
from pytestqt.qt_compat import QStandardItemModel, QStandardItem, \
    QFileSystemModel, QStringListModel, QSortFilterProxyModel, QT_API, QtCore

pytestmark = pytest.mark.usefixtures('qtbot')

skip_due_to_pyside_private_methods = pytest.mark.skipif(
    QT_API == 'pyside', reason='Skip tests that work with QAbstractItemModel '
                               'subclasses on PySide because methods that '
                               'should be public are private. See'
                               'PySide/PySide#127.')


@pytest.fixture(autouse=True)
def default_model_implementations_return_qvariant(qtmodeltester):
    """PyQt4 is the only implementation where the builtin model implementations
    may return QVariant objects.
    """
    qtmodeltester.data_may_return_qvariant = QT_API == 'pyqt4'


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


@skip_due_to_pyside_private_methods
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
@skip_due_to_pyside_private_methods
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


@pytest.mark.parametrize('role, should_pass', [
    (QtCore.Qt.AlignLeft, True),
    (QtCore.Qt.AlignRight, True),
    (0xFFFFFF, False),
])
@skip_due_to_pyside_private_methods
def test_data_alignment(testdir, role, should_pass):
    """Test a custom model which returns a good and alignments from data().
    qtmodeltest should capture this problem and fail when that happens.
    """
    testdir.makepyfile('''
        from pytestqt.qt_compat import QAbstractListModel, QtCore

        invalid_obj = object()  # This will fail the type check for any role

        class MyModel(QAbstractListModel):

            def rowCount(self, parent=QtCore.QModelIndex()):
                return 1 if parent == QtCore.QModelIndex() else 0

            def columnCount(self, parent=QtCore.QModelIndex()):
                return 1 if parent == QtCore.QModelIndex() else 0

            def data(self, index=QtCore.QModelIndex(),
                     role=QtCore.Qt.DisplayRole):
                if role == QtCore.Qt.TextAlignmentRole:
                    return {role}
                else:
                    if role == QtCore.Qt.DisplayRole and index == \
                        self.index(0, 0):
                        return 'Hello'
                return None

        def test_broken_alignment(qtmodeltester):
            model = MyModel()
            qtmodeltester.data_may_return_qvariant = True
            qtmodeltester.check(model)
    '''.format(role=role))
    res = testdir.inline_run()
    res.assertoutcome(passed=int(should_pass), failed=int(not should_pass))
