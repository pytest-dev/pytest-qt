import pytest

from pytestqt.qt_compat import qt_api
from pytestqt import modeltest

pytestmark = pytest.mark.usefixtures("qtbot")


class BasicModel(qt_api.QtCore.QAbstractItemModel):
    def data(self, index, role=qt_api.QtCore.Qt.DisplayRole):
        return None

    def rowCount(self, parent=qt_api.QtCore.QModelIndex()):
        return 0

    def columnCount(self, parent=qt_api.QtCore.QModelIndex()):
        return 0

    def index(self, row, column, parent=qt_api.QtCore.QModelIndex()):
        return qt_api.QtCore.QModelIndex()

    def parent(self, index):
        return qt_api.QtCore.QModelIndex()


def test_standard_item_model(qtmodeltester):
    """
    Basic test which uses qtmodeltester with a qt_api.QStandardItemModel.
    """
    model = qt_api.QStandardItemModel()
    items = [qt_api.QStandardItem(str(i)) for i in range(6)]
    model.setItem(0, 0, items[0])
    model.setItem(0, 1, items[1])
    model.setItem(1, 0, items[2])
    model.setItem(1, 1, items[3])

    items[0].setChild(0, items[4])
    items[4].setChild(0, items[5])

    qtmodeltester.check(model, force_py=True)


def test_string_list_model(qtmodeltester):
    model = qt_api.QStringListModel()
    model.setStringList(["hello", "world"])
    qtmodeltester.check(model, force_py=True)


def test_sort_filter_proxy_model(qtmodeltester):
    model = qt_api.QStringListModel()
    model.setStringList(["hello", "world"])
    proxy = qt_api.QSortFilterProxyModel()
    proxy.setSourceModel(model)
    qtmodeltester.check(proxy, force_py=True)


@pytest.mark.parametrize(
    "broken_role",
    [
        qt_api.QtCore.Qt.ToolTipRole,
        qt_api.QtCore.Qt.StatusTipRole,
        qt_api.QtCore.Qt.WhatsThisRole,
        qt_api.QtCore.Qt.SizeHintRole,
        qt_api.QtCore.Qt.FontRole,
        qt_api.QtCore.Qt.BackgroundColorRole,
        qt_api.QtCore.Qt.TextColorRole,
        qt_api.QtCore.Qt.TextAlignmentRole,
        qt_api.QtCore.Qt.CheckStateRole,
    ],
)
def test_broken_types(check_model, broken_role):
    """
    Check that qtmodeltester correctly captures data() returning invalid
    values for various display roles.
    """

    class BrokenTypeModel(qt_api.QAbstractListModel):
        def rowCount(self, parent=qt_api.QtCore.QModelIndex()):
            if parent == qt_api.QtCore.QModelIndex():
                return 1
            else:
                return 0

        def data(
            self, index=qt_api.QtCore.QModelIndex(), role=qt_api.QtCore.Qt.DisplayRole
        ):
            if role == broken_role:
                return object()  # This will fail the type check for any role
            else:
                return None

    check_model(BrokenTypeModel(), should_pass=False)


@pytest.mark.parametrize(
    "role_value, should_pass",
    [
        (qt_api.QtCore.Qt.AlignLeft, True),
        (qt_api.QtCore.Qt.AlignRight, True),
        (0xFFFFFF, False),
        ("foo", False),
        (object(), False),
    ],
)
def test_data_alignment(role_value, should_pass, check_model):
    """Test a custom model which returns a good and alignments from data().
    qtmodeltest should capture this problem and fail when that happens.
    """

    class MyModel(qt_api.QAbstractListModel):
        def rowCount(self, parent=qt_api.QtCore.QModelIndex()):
            return 1 if parent == qt_api.QtCore.QModelIndex() else 0

        def data(
            self, index=qt_api.QtCore.QModelIndex(), role=qt_api.QtCore.Qt.DisplayRole
        ):
            if role == qt_api.QtCore.Qt.TextAlignmentRole:
                return role_value
            elif role == qt_api.QtCore.Qt.DisplayRole:
                if index == self.index(0, 0):
                    return "Hello"
            return None

    check_model(MyModel(), should_pass=should_pass)


def test_header_handling(check_model):
    class MyModel(qt_api.QAbstractListModel):
        def rowCount(self, parent=qt_api.QtCore.QModelIndex()):
            return 1 if parent == qt_api.QtCore.QModelIndex() else 0

        def set_header_text(self, header):
            self._header_text = header
            self.headerDataChanged.emit(qt_api.QtCore.Qt.Vertical, 0, 0)
            self.headerDataChanged.emit(qt_api.QtCore.Qt.Horizontal, 0, 0)

        def headerData(self, section, orientation, role=qt_api.QtCore.Qt.DisplayRole):
            return self._header_text

        def data(
            self, index=qt_api.QtCore.QModelIndex(), role=qt_api.QtCore.Qt.DisplayRole
        ):
            if role == qt_api.QtCore.Qt.DisplayRole and index == self.index(0, 0):
                return "Contents"
            return None

    model = MyModel()
    model.set_header_text("Start Header")
    check_model(model, should_pass=True)
    model.set_header_text("New Header")


@pytest.fixture
def check_model(qtmodeltester):
    """
    Return a check_model(model, should_pass=True) function that uses
    qtmodeltester to check if the model is OK or not according to the
    ``should_pass`` parameter.
    """

    def check(model, should_pass=True):
        if should_pass:
            qtmodeltester.check(model, force_py=True)
        else:
            with pytest.raises(AssertionError):
                qtmodeltester.check(model, force_py=True)

    return check


def test_invalid_column_count(qtmodeltester):
    """Basic check with an invalid model."""

    class Model(BasicModel):
        def columnCount(self, parent=qt_api.QtCore.QModelIndex()):
            return -1

    model = Model()

    with pytest.raises(AssertionError):
        qtmodeltester.check(model, force_py=True)


def test_changing_model_insert(qtmodeltester):
    model = qt_api.QStandardItemModel()
    item = qt_api.QStandardItem("foo")
    qtmodeltester.check(model, force_py=True)
    model.insertRow(0, item)


def test_changing_model_remove(qtmodeltester):
    model = qt_api.QStandardItemModel()
    item = qt_api.QStandardItem("foo")
    model.setItem(0, 0, item)
    qtmodeltester.check(model, force_py=True)
    model.removeRow(0)


def test_changing_model_data(qtmodeltester):
    model = qt_api.QStandardItemModel()
    item = qt_api.QStandardItem("foo")
    model.setItem(0, 0, item)
    qtmodeltester.check(model, force_py=True)
    model.setData(model.index(0, 0), "hello world")


@pytest.mark.parametrize(
    "orientation", [qt_api.QtCore.Qt.Horizontal, qt_api.QtCore.Qt.Vertical]
)
def test_changing_model_header_data(qtmodeltester, orientation):
    model = qt_api.QStandardItemModel()
    item = qt_api.QStandardItem("foo")
    model.setItem(0, 0, item)
    qtmodeltester.check(model, force_py=True)
    model.setHeaderData(0, orientation, "blah")


def test_changing_model_sort(qtmodeltester):
    """Sorting emits layoutChanged"""
    model = qt_api.QStandardItemModel()
    item = qt_api.QStandardItem("foo")
    model.setItem(0, 0, item)
    qtmodeltester.check(model, force_py=True)
    model.sort(0)


def test_nop(qtmodeltester):
    """We should not get a crash on cleanup with no model."""
    pass


def test_overridden_methods(qtmodeltester):
    """Make sure overriden methods of a model are actually run.

    With a previous implementation of the modeltester using sip.cast, the custom
    implementations did never actually run.
    """

    class Model(BasicModel):
        def __init__(self, parent=None):
            super(Model, self).__init__(parent)
            self.row_count_did_run = False

        def rowCount(self, parent=None):
            self.row_count_did_run = True
            return 0

    model = Model()
    assert not model.row_count_did_run
    qtmodeltester.check(model, force_py=True)
    assert model.row_count_did_run


def test_fetch_more(qtmodeltester):
    class Model(qt_api.QStandardItemModel):
        def canFetchMore(self, parent):
            return True

        def fetchMore(self, parent):
            """Force a re-check while fetching more."""
            self.setData(self.index(0, 0), "bar")

    model = Model()
    item = qt_api.QStandardItem("foo")
    model.setItem(0, 0, item)
    qtmodeltester.check(model, force_py=True)


def test_invalid_parent(qtmodeltester):
    class Model(qt_api.QStandardItemModel):
        def parent(self, index):
            if index == self.index(0, 0, parent=self.index(0, 0)):
                return self.index(0, 0)
            else:
                return qt_api.QtCore.QModelIndex()

    model = Model()
    item = qt_api.QStandardItem("foo")
    item2 = qt_api.QStandardItem("bar")
    item3 = qt_api.QStandardItem("bar")
    model.setItem(0, 0, item)
    item.setChild(0, item2)
    item2.setChild(0, item3)

    with pytest.raises(AssertionError):
        qtmodeltester.check(model, force_py=True)


@pytest.mark.skipif(not modeltest.HAS_QT_TESTER, reason="No Qt modeltester available")
def test_qt_tester_valid(testdir):
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api
        from pytestqt import modeltest

        assert modeltest.HAS_QT_TESTER


        def test_ok(qtmodeltester):
            model = qt_api.QStandardItemModel()
            qtmodeltester.check(model)
        """
    )
    res = testdir.inline_run()
    res.assertoutcome(passed=1, failed=0)


@pytest.mark.skipif(not modeltest.HAS_QT_TESTER, reason="No Qt modeltester available")
def test_qt_tester_invalid(testdir):
    testdir.makeini(
        """
        [pytest]
        qt_log_level_fail = NO
    """
    )
    testdir.makepyfile(
        """
        from pytestqt.qt_compat import qt_api
        from pytestqt import modeltest

        assert modeltest.HAS_QT_TESTER


        class Model(qt_api.QtCore.QAbstractItemModel):
            def data(self, index, role=qt_api.QtCore.Qt.DisplayRole):
                return None

            def rowCount(self, parent=qt_api.QtCore.QModelIndex()):
                return 0

            def columnCount(self, parent=qt_api.QtCore.QModelIndex()):
                return -1

            def index(self, row, column, parent=qt_api.QtCore.QModelIndex()):
                return qt_api.QtCore.QModelIndex()

            def parent(self, index):
                return qt_api.QtCore.QModelIndex()


        def test_ok(qtmodeltester):
            model = Model()
            qtmodeltester.check(model)
        """
    )
    res = testdir.runpytest()
    res.stdout.fnmatch_lines(
        [
            "*__ test_ok __*",
            "test_qt_tester_invalid.py:*: Qt modeltester errors",
            "*-- Captured Qt messages --*",
            "* QtWarningMsg: FAIL! model->columnCount(QModelIndex()) >= 0 () returned FALSE "
            "(qabstractitemmodeltester.cpp:*)",
            "*-- Captured stdout call --*",
            "modeltest: Using Qt C++ tester",
            "*== 1 failed in * ==*",
        ]
    )
