# This file is based on the original C++ modeltest.cpp from:
# http://code.qt.io/cgit/qt/qtbase.git/tree/tests/auto/other/modeltest/modeltest.cpp
# Licensed under the following terms:
#
# Copyright (C) 2015 The Qt Company Ltd.
# Contact: http://www.qt.io/licensing/
#
# This file is part of the test suite of the Qt Toolkit.
#
# $QT_BEGIN_LICENSE:LGPL21$
# Commercial License Usage
# Licensees holding valid commercial Qt licenses may use this file in
# accordance with the commercial license agreement provided with the
# Software or, alternatively, in accordance with the terms contained in
# a written agreement between you and The Qt Company. For licensing terms
# and conditions see http://www.qt.io/terms-conditions. For further
# information use the contact form at http://www.qt.io/contact-us.
#
# GNU Lesser General Public License Usage
# Alternatively, this file may be used under the terms of the GNU Lesser
# General Public License version 2.1 or version 3 as published by the Free
# Software Foundation and appearing in the file LICENSE.LGPLv21 and
# LICENSE.LGPLv3 included in the packaging of this file. Please review the
# following information to ensure the GNU Lesser General Public License
# requirements will be met: https://www.gnu.org/licenses/lgpl.html and
# http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
#
# As a special exception, The Qt Company gives you certain additional
# rights. These rights are described in The Qt Company LGPL Exception
# version 1.1, included in the file LGPL_EXCEPTION.txt in this package.
#
# $QT_END_LICENSE$

from __future__ import print_function
import collections

from pytestqt.qt_compat import qt_api


_Changing = collections.namedtuple('_Changing', 'parent, old_size, last, next')


class ModelTester:

    """A tester for Qt's QAbstractItemModels.

    :ivar bool data_display_may_return_none: if the model implementation is
        allowed to return None from data() for DisplayRole.
    """

    def __init__(self, config):
        self._model = None
        self._fetching_more = None
        self._insert = None
        self._remove = None
        self._changing = []
        self.data_display_may_return_none = False

    def _debug(self, text):
        print('modeltest: ' + text)

    def _modelindex_debug(self, index):
        """Get a string for debug output for a QModelIndex."""
        if not index.isValid():
            return '<invalid> (0x{:x})'.format(id(index))
        else:
            data = self._model.data(index, qt_api.QtCore.Qt.DisplayRole)
            return '{}/{} {!r} (0x{:x})'.format(
                index.row(), index.column(),
                qt_api.extract_from_variant(data),
                id(index))

    def check(self, model):
        """Runs a series of checks in the given model.

        Connect to all of the models signals.

        Whenever anything happens recheck everything.
        """
        assert model is not None
        self._model = model
        self._fetching_more = False
        self._insert = []
        self._remove = []
        self._changing = []

        self._model.columnsAboutToBeInserted.connect(self._run)
        self._model.columnsAboutToBeRemoved.connect(self._run)
        self._model.columnsInserted.connect(self._run)
        self._model.columnsRemoved.connect(self._run)
        self._model.dataChanged.connect(self._run)
        self._model.headerDataChanged.connect(self._run)
        self._model.layoutAboutToBeChanged.connect(self._run)
        self._model.layoutChanged.connect(self._run)
        self._model.modelReset.connect(self._run)
        self._model.rowsAboutToBeInserted.connect(self._run)
        self._model.rowsAboutToBeRemoved.connect(self._run)
        self._model.rowsInserted.connect(self._run)
        self._model.rowsRemoved.connect(self._run)

        # Special checks for changes
        self._model.layoutAboutToBeChanged.connect(
            self._on_layout_about_to_be_changed)
        self._model.layoutChanged.connect(self._on_layout_changed)
        self._model.rowsAboutToBeInserted.connect(
            self._on_rows_about_to_be_inserted)
        self._model.rowsAboutToBeRemoved.connect(
            self._on_rows_about_to_be_removed)
        self._model.rowsInserted.connect(self._on_rows_inserted)
        self._model.rowsRemoved.connect(self._on_rows_removed)
        self._model.dataChanged.connect(self._on_data_changed)
        self._model.headerDataChanged.connect(self._on_header_data_changed)

        self._run()

    def _cleanup(self):
        """Not API intended for users, but called from the fixture function."""
        if self._model is None:
            return

        self._model.columnsAboutToBeInserted.disconnect(self._run)
        self._model.columnsAboutToBeRemoved.disconnect(self._run)
        self._model.columnsInserted.disconnect(self._run)
        self._model.columnsRemoved.disconnect(self._run)
        self._model.dataChanged.disconnect(self._run)
        self._model.headerDataChanged.disconnect(self._run)
        self._model.layoutAboutToBeChanged.disconnect(self._run)
        self._model.layoutChanged.disconnect(self._run)
        self._model.modelReset.disconnect(self._run)
        self._model.rowsAboutToBeInserted.disconnect(self._run)
        self._model.rowsAboutToBeRemoved.disconnect(self._run)
        self._model.rowsInserted.disconnect(self._run)
        self._model.rowsRemoved.disconnect(self._run)

        self._model.layoutAboutToBeChanged.disconnect(
            self._on_layout_about_to_be_changed)
        self._model.layoutChanged.disconnect(self._on_layout_changed)
        self._model.rowsAboutToBeInserted.disconnect(
            self._on_rows_about_to_be_inserted)
        self._model.rowsAboutToBeRemoved.disconnect(
            self._on_rows_about_to_be_removed)
        self._model.rowsInserted.disconnect(self._on_rows_inserted)
        self._model.rowsRemoved.disconnect(self._on_rows_removed)
        self._model.dataChanged.disconnect(self._on_data_changed)
        self._model.headerDataChanged.disconnect(self._on_header_data_changed)

        self._model = None

    def _run(self):
        assert self._model is not None
        assert self._fetching_more is not None
        if self._fetching_more:
            return
        self._test_basic()
        self._test_row_count()
        self._test_column_count()
        self._test_has_index()
        self._test_index()
        self._test_parent()
        self._test_data()

    def _test_basic(self):
        """Try to call a number of the basic functions (not all).

        Make sure the model doesn't outright segfault, testing the functions
        which make sense.
        """
        assert self._model.buddy(qt_api.QtCore.QModelIndex()) == qt_api.QtCore.QModelIndex()
        self._model.canFetchMore(qt_api.QtCore.QModelIndex())
        assert self._column_count(qt_api.QtCore.QModelIndex()) >= 0
        display_data = self._model.data(qt_api.QtCore.QModelIndex(),
                                        qt_api.QtCore.Qt.DisplayRole)

        assert qt_api.extract_from_variant(display_data) is None
        self._fetch_more(qt_api.QtCore.QModelIndex())
        flags = self._model.flags(qt_api.QtCore.QModelIndex())
        assert flags == qt_api.QtCore.Qt.ItemIsDropEnabled or not flags
        self._has_children(qt_api.QtCore.QModelIndex())
        self._model.hasIndex(0, 0)
        self._model.headerData(0, qt_api.QtCore.Qt.Horizontal)
        self._model.index(0, 0)
        self._model.itemData(qt_api.QtCore.QModelIndex())
        cache = None
        self._model.match(qt_api.QtCore.QModelIndex(), -1, cache)
        self._model.mimeTypes()
        assert self._parent(qt_api.QtCore.QModelIndex()) == qt_api.QtCore.QModelIndex()
        assert self._model.rowCount() >= 0
        self._model.setData(qt_api.QtCore.QModelIndex(), None, -1)
        self._model.setHeaderData(-1, qt_api.QtCore.Qt.Horizontal, None)
        self._model.setHeaderData(999999, qt_api.QtCore.Qt.Horizontal, None)
        self._model.sibling(0, 0, qt_api.QtCore.QModelIndex())
        self._model.span(qt_api.QtCore.QModelIndex())
        self._model.supportedDropActions()

    def _test_row_count(self):
        """Test model's implementation of rowCount() and hasChildren().

        Models that are dynamically populated are not as fully tested here.

        The models rowCount() is tested more extensively in _check_children(),
        but this catches the big mistakes.
        """
        # check top row
        top_index = self._model.index(0, 0, qt_api.QtCore.QModelIndex())
        rows = self._model.rowCount(top_index)
        assert rows >= 0
        if rows > 0:
            assert self._has_children(top_index)

        second_level_index = self._model.index(0, 0, top_index)
        if second_level_index.isValid():  # not the top level
            # check a row count where parent is valid
            rows = self._model.rowCount(second_level_index)
            assert rows >= 0
            if rows > 0:
                assert self._has_children(second_level_index)

    def _test_column_count(self):
        """Test model's implementation of columnCount() and hasChildren().

        columnCount() is tested more extensively in _check_children(),
        but this catches the big mistakes.
        """
        # check top row
        top_index = self._model.index(0, 0, qt_api.QtCore.QModelIndex())
        assert self._column_count(top_index) >= 0

        # check a column count where parent is valid
        child_index = self._model.index(0, 0, top_index)
        if child_index.isValid():
            assert self._column_count(child_index) >= 0

    def _test_has_index(self):
        """Test model's implementation of hasIndex().

        hasIndex() is tested more extensively in _check_children(),
        but this catches the big mistakes.
        """
        # Make sure that invalid values return an invalid index
        assert not self._model.hasIndex(-2, -2)
        assert not self._model.hasIndex(-2, 0)
        assert not self._model.hasIndex(0, -2)

        rows = self._model.rowCount()
        columns = self._column_count()

        # check out of bounds
        assert not self._model.hasIndex(rows, columns)
        assert not self._model.hasIndex(rows + 1, columns + 1)

        if rows > 0:
            assert self._model.hasIndex(0, 0)

    def _test_index(self):
        """Test model's implementation of index().

        index() is tested more extensively in _check_children(),
        but this catches the big mistakes.
        """
        # Make sure that invalid values return an invalid index
        assert self._model.index(-2, -2) == qt_api.QtCore.QModelIndex()
        assert self._model.index(-2, 0) == qt_api.QtCore.QModelIndex()
        assert self._model.index(0, -2) == qt_api.QtCore.QModelIndex()

        rows = self._model.rowCount()
        columns = self._column_count()

        if rows == 0:
            return

        # Catch off by one errors
        assert self._model.index(rows, columns) == qt_api.QtCore.QModelIndex()
        assert self._model.index(0, 0).isValid()

        # Make sure that the same index is *always* returned
        a = self._model.index(0, 0)
        b = self._model.index(0, 0)
        assert a == b

    def _test_parent(self):
        """Tests model's implementation of QAbstractItemModel::parent()."""
        # Make sure the model won't crash and will return an invalid
        # QModelIndex when asked for the parent of an invalid index.
        assert self._parent(qt_api.QtCore.QModelIndex()) == qt_api.QtCore.QModelIndex()

        if self._model.rowCount() == 0:
            return

        # Column 0                | Column 1      |
        # QModelIndex()           |               |
        #    \- top_index         | top_index_1   |
        #         \- child_index  | child_index_1 |

        # Common error test #1, make sure that a top level index has a parent
        # that is a invalid QModelIndex.
        top_index = self._model.index(0, 0, qt_api.QtCore.QModelIndex())
        assert self._parent(top_index) == qt_api.QtCore.QModelIndex()

        # Common error test #2, make sure that a second level index has a
        # parent that is the first level index.
        if self._model.rowCount(top_index) > 0:
            child_index = self._model.index(0, 0, top_index)
            assert self._parent(child_index) == top_index

        # Common error test #3, the second column should NOT have the same
        # children as the first column in a row.
        # Usually the second column shouldn't have children.
        top_index_1 = self._model.index(0, 1, qt_api.QtCore.QModelIndex())
        if self._model.rowCount(top_index_1) > 0:
            child_index = self._model.index(0, 0, top_index)
            child_index_1 = self._model.index(0, 0, top_index_1)
            assert child_index != child_index_1

        # Full test, walk n levels deep through the model making sure that all
        # parent's children correctly specify their parent.
        self._check_children(qt_api.QtCore.QModelIndex())

    def _check_children(self, parent, current_depth=0):
        """Check parent/children relationships.

        Called from the parent() test.

        A model that returns an index of parent X should also return X when
        asking for the parent of the index.

        This recursive function does pretty extensive testing on the whole
        model in an effort to catch edge cases.

        This function assumes that rowCount(), columnCount() and index()
        already work.  If they have a bug it will point it out, but the above
        tests should have already found the basic bugs because it is easier to
        figure out the problem in those tests then this one.
        """
        # First just try walking back up the tree.
        p = parent
        while p.isValid():
            p = p.parent()

        # For models that are dynamically populated
        if self._model.canFetchMore(parent):
            self._fetch_more(parent)

        rows = self._model.rowCount(parent)
        columns = self._column_count(parent)

        if rows > 0:
            assert self._has_children(parent)

        # Some further testing against rows(), columns(), and hasChildren()
        assert rows >= 0
        assert columns >= 0
        if rows > 0:
            assert self._has_children(parent)
        self._debug("Checking children of {} with depth {} "
                    "({} rows, {} columns)".format(
                        self._modelindex_debug(parent), current_depth,
                        rows, columns))

        top_left_child = self._model.index(0, 0, parent)

        assert not self._model.hasIndex(rows + 1, 0, parent)
        for r in range(rows):
            if self._model.canFetchMore(parent):
                self._fetch_more(parent)
            assert not self._model.hasIndex(r, columns + 1, parent)
            for c in range(columns):
                assert self._model.hasIndex(r, c, parent)
                index = self._model.index(r, c, parent)
                # rowCount() and columnCount() said that it existed...
                assert index.isValid()

                # index() should always return the same index when called twice
                # in a row
                modified_index = self._model.index(r, c, parent)
                assert index == modified_index

                # Make sure we get the same index if we request it twice in a
                # row
                a = self._model.index(r, c, parent)
                b = self._model.index(r, c, parent)
                assert a == b

                sibling = self._model.sibling(r, c, top_left_child)
                assert index == sibling

                sibling = top_left_child.sibling(r, c)
                assert index == sibling

                # Some basic checking on the index that is returned
                assert index.model() == self._model
                assert index.row() == r
                assert index.column() == c

                data = self._model.data(index, qt_api.QtCore.Qt.DisplayRole)
                if not self.data_display_may_return_none:
                    assert qt_api.extract_from_variant(data) is not None

                # If the next test fails here is some somewhat useful debug you
                # play with.

                if self._parent(index) != parent:
                    self._debug(
                        "parent-check failed for index {}:\n"
                        "  parent {} != expected {}".format(
                            self._modelindex_debug(index),
                            self._modelindex_debug(self._parent(index)),
                            self._modelindex_debug(parent)
                        )
                    )

                # Check that we can get back our real parent.
                assert self._parent(index) == parent

                # recursively go down the children
                if self._has_children(index) and current_depth < 10:
                    self._debug("{} has {} children".format(
                        self._modelindex_debug(index),
                        self._model.rowCount(index)
                    ))
                    self._check_children(index, current_depth + 1)

                # make sure that after testing the children that the index
                # doesn't change.
                newer_index = self._model.index(r, c, parent)
                assert index == newer_index
        self._debug("Children check for {} done".format(self._modelindex_debug(parent)))

    def _test_data(self):
        """Test model's implementation of data()"""
        # Invalid index should return an invalid qvariant
        value = self._model.data(qt_api.QtCore.QModelIndex(), qt_api.QtCore.Qt.DisplayRole)
        assert qt_api.extract_from_variant(value) is None

        if self._model.rowCount() == 0:
            return

        # A valid index should have a valid QVariant data
        assert self._model.index(0, 0).isValid()

        # shouldn't be able to set data on an invalid index
        ok = self._model.setData(qt_api.QtCore.QModelIndex(), "foo",
                                 qt_api.QtCore.Qt.DisplayRole)
        assert not ok

        types = [
            (qt_api.QtCore.Qt.ToolTipRole, str),
            (qt_api.QtCore.Qt.StatusTipRole, str),
            (qt_api.QtCore.Qt.WhatsThisRole, str),
            (qt_api.QtCore.Qt.SizeHintRole, qt_api.QtCore.QSize),
            (qt_api.QtCore.Qt.FontRole, qt_api.QtGui.QFont),
            (qt_api.QtCore.Qt.BackgroundColorRole, (qt_api.QtGui.QColor, qt_api.QtGui.QBrush)),
            (qt_api.QtCore.Qt.TextColorRole, (qt_api.QtGui.QColor, qt_api.QtGui.QBrush)),
        ]

        # General purpose roles with a fixed expected type
        for role, typ in types:
            data = self._model.data(self._model.index(0, 0), role)
            assert data == None or isinstance(data, typ), role

        # Check that the alignment is one we know about
        alignment = self._model.data(self._model.index(0, 0),
                                     qt_api.QtCore.Qt.TextAlignmentRole)
        alignment = qt_api.extract_from_variant(alignment)
        if alignment is not None:
            try:
                alignment = int(alignment)
            except (TypeError, ValueError):
                assert 0, '%r should be a TextAlignmentRole enum' % alignment
            mask = int(qt_api.QtCore.Qt.AlignHorizontal_Mask |
                       qt_api.QtCore.Qt.AlignVertical_Mask)
            assert alignment == alignment & mask

        # Check that the "check state" is one we know about.
        state = self._model.data(self._model.index(0, 0),
                                 qt_api.QtCore.Qt.CheckStateRole)
        assert state in [None, qt_api.QtCore.Qt.Unchecked, qt_api.QtCore.Qt.PartiallyChecked,
                         qt_api.QtCore.Qt.Checked]

    def _on_rows_about_to_be_inserted(self, parent, start, end):
        """Store what is about to be inserted.

        This gets stored to make sure it actually happens in rowsInserted.
        """
        last_index = self._model.index(start - 1, 0, parent)
        next_index = self._model.index(start, 0, parent)
        parent_rowcount = self._model.rowCount(parent)

        self._debug("rows about to be inserted: start {}, end {}, parent {}, "
                    "parent row count {}, last item {}, next item {}".format(
                        start, end,
                        self._modelindex_debug(parent),
                        parent_rowcount,
                        self._modelindex_debug(last_index),
                        self._modelindex_debug(next_index),
                    )
        )

        last_data = self._model.data(last_index)
        next_data = self._model.data(next_index)
        c = _Changing(parent=parent, old_size=parent_rowcount,
                      last=last_data, next=next_data)
        self._insert.append(c)

    def _on_rows_inserted(self, parent, start, end):
        """Confirm that what was said was going to happen actually did."""
        c = self._insert.pop()
        last_data = self._model.data(self._model.index(start - 1, 0, parent))
        next_data = self._model.data(self._model.index(end + 1, 0, c.parent))
        expected_size = c.old_size + (end - start + 1)
        current_size = self._model.rowCount(parent)

        self._debug("rows inserted: start {}, end {}".format(start, end))
        self._debug("  from rowsAboutToBeInserted: parent {}, "
                    "size {} (-> {} expected), "
                    "next data {!r}, last data {!r}".format(
                        self._modelindex_debug(c.parent),
                        c.old_size, expected_size,
                        qt_api.extract_from_variant(c.next),
                        qt_api.extract_from_variant(c.last)
                    )
        )

        self._debug("  now in rowsInserted:        parent {}, size {}, "
                    "next data {!r}, last data {!r}".format(
                        self._modelindex_debug(parent),
                        current_size,
                        qt_api.extract_from_variant(next_data),
                        qt_api.extract_from_variant(last_data)
                    )
        )

        if not qt_api.QtCore.qVersion().startswith('4.'):
            # Skipping this on Qt4 as the parent changes for some reason:
            # modeltest: rows about to be inserted: [...]
            #            parent <invalid> (0x7f8f540eacf8), [...]
            # [...]
            # modeltest: from rowsAboutToBeInserted:
            #            parent 0/0 None (0x7f8f540eacf8), [...]
            # modeltest: now in rowsInserted:
            #            parent <invalid> (0x7f8f60a96cf8) [...]
            assert c.parent == parent

        for ii in range(start, end + 1):
            idx = self._model.index(ii, 0, parent)
            self._debug(" item {} inserted: {}".format(ii,
                                                       self._modelindex_debug(idx)))
        self._debug('')

        assert current_size == expected_size
        assert c.last == last_data
        assert c.next == next_data

    def _on_layout_about_to_be_changed(self):
        for i in range(max(self._model.rowCount(), 100)):
            idx = qt_api.QtCore.QPersistentModelIndex(self._model.index(i, 0))
            self._changing.append(idx)

    def _on_layout_changed(self):
        for p in self._changing:
            assert p == self._model.index(p.row(), p.column(), p.parent())
        self._changing = []

    def _on_rows_about_to_be_removed(self, parent, start, end):
        """Store what is about to be removed to make sure it actually happens.

        This gets stored to make sure it actually happens in rowsRemoved.
        """
        last_index = self._model.index(start - 1, 0, parent)
        next_index = self._model.index(end + 1, 0, parent)
        parent_rowcount = self._model.rowCount(parent)

        self._debug("rows about to be removed: start {}, end {}, parent {}, "
                    "parent row count {}, last item {}, next item {}".format(
                        start, end,
                        self._modelindex_debug(parent),
                        parent_rowcount,
                        self._modelindex_debug(last_index),
                        self._modelindex_debug(next_index),
                    )
        )

        last_data = self._model.data(last_index)
        next_data = self._model.data(next_index)
        c = _Changing(parent=parent, old_size=parent_rowcount,
                      last=last_data, next=next_data)
        self._remove.append(c)

    def _on_rows_removed(self, parent, start, end):
        """Confirm that what was said was going to happen actually did."""
        c = self._remove.pop()
        last_data = self._model.data(self._model.index(start - 1, 0, c.parent))
        next_data = self._model.data(self._model.index(start, 0, c.parent))
        current_size = self._model.rowCount(parent)
        expected_size = c.old_size - (end - start + 1)

        self._debug("rows removed: start {}, end {}".format(start, end))
        self._debug("  from rowsAboutToBeRemoved: parent {}, "
                    "size {} (-> {} expected), "
                    "next data {!r}, last data {!r}".format(
                        self._modelindex_debug(c.parent),
                        c.old_size, expected_size,
                        qt_api.extract_from_variant(c.next),
                        qt_api.extract_from_variant(c.last)
                    )
        )

        self._debug("  now in rowsRemoved:        parent {}, size {}, "
                    "next data {!r}, last data {!r}".format(
                        self._modelindex_debug(parent),
                        current_size,
                        qt_api.extract_from_variant(next_data),
                        qt_api.extract_from_variant(last_data)
                    )
        )

        if not qt_api.QtCore.qVersion().startswith('4.'):
            # Skipping this on Qt4 as the parent changes for some reason
            # see _on_rows_inserted for details
            assert c.parent == parent

        assert current_size == expected_size
        assert c.last == last_data
        assert c.next == next_data

    def _on_data_changed(self, top_left, bottom_right):
        assert top_left.isValid()
        assert bottom_right.isValid()
        common_parent = bottom_right.parent()
        assert top_left.parent() == common_parent
        assert top_left.row() <= bottom_right.row()
        assert top_left.column() <= bottom_right.column()
        row_count = self._model.rowCount(common_parent)
        column_count = self._column_count(common_parent)
        assert bottom_right.row() < row_count
        assert bottom_right.column() < column_count

    def _on_header_data_changed(self, orientation, start, end):
        assert orientation in [qt_api.QtCore.Qt.Horizontal, qt_api.QtCore.Qt.Vertical]
        assert start >= 0
        assert end >= 0
        assert start <= end
        if orientation == qt_api.QtCore.Qt.Vertical:
            item_count = self._model.rowCount()
        else:
            item_count = self._column_count()
        assert start < item_count
        assert end < item_count

    def _column_count(self, parent=qt_api.QtCore.QModelIndex()):
        """
        Workaround for the fact that ``columnCount`` is a private method in
        QAbstractListModel/QAbstractTableModel subclasses.
        """
        if isinstance(self._model, qt_api.QAbstractListModel):
            return 1 if parent == qt_api.QtCore.QModelIndex() else 0
        else:
            return self._model.columnCount(parent)

    def _parent(self, index):
        """
        .. see:: ``_column_count``
        """
        model_types = (qt_api.QAbstractListModel, qt_api.QAbstractTableModel)
        if isinstance(self._model, model_types):
            return qt_api.QtCore.QModelIndex()
        else:
            return self._model.parent(index)

    def _has_children(self, parent=qt_api.QtCore.QModelIndex()):
        """
        .. see:: ``_column_count``
        """
        model_types = (qt_api.QAbstractListModel, qt_api.QAbstractTableModel)
        if isinstance(self._model, model_types):
            return parent == qt_api.QtCore.QModelIndex() and self._model.rowCount() > 0
        else:
            return self._model.hasChildren(parent)

    def _fetch_more(self, parent):
        """Call ``fetchMore`` on the model and set ``self._fetching_more``."""
        self._fetching_more = True
        self._model.fetchMore(parent)
        self._fetching_more = False
