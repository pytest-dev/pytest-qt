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

from pytestqt.qt_compat import QtCore, QtGui, cast, extract_from_variant


_Changing = collections.namedtuple('_Changing', 'parent, oldSize, last, next')


class ModelTester:

    """A tester for Qt's QAbstractItemModel's."""

    def __init__(self, config):
        self._model = None
        self._orig_model = None
        self._fetching_more = None
        self._insert = None
        self._remove = None
        self._verbose = config.getoption('verbose') > 0

    def _debug(self, *args):
        if self._verbose:
            print(*args)

    def check(self, model, verbose=False):
        """Runs a series of checks in the given model.

        Connect to all of the models signals.

        Whenever anything happens recheck everything.
        """
        assert model is not None
        self._model = cast(model, QtCore.QAbstractItemModel)
        self._orig_model = model
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

        self._run(verbose=verbose)

    def _cleanup(self):
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
        self._orig_model = None

    def _run(self, verbose=False):
        self._verbose = verbose
        assert self._model is not None
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
        """
        Try to call a number of the basic functions (not all).

        Make sure the model doesn't outright segfault, testing the functions
        that makes sense.
        """
        assert self._model.buddy(QtCore.QModelIndex()) == QtCore.QModelIndex()
        self._model.canFetchMore(QtCore.QModelIndex())
        assert self._model.columnCount(QtCore.QModelIndex()) >= 0
        display_data = self._model.data(QtCore.QModelIndex(),
                                        QtCore.Qt.DisplayRole)

        # note: compare against None using "==" on purpose, as depending
        # on the Qt API this will be a QVariant object which compares using
        # "==" correctly against other Python types, including None
        assert display_data == None
        self._fetching_more = True
        self._model.fetchMore(QtCore.QModelIndex())
        self._fetching_more = False
        flags = self._model.flags(QtCore.QModelIndex())
        assert flags == QtCore.Qt.ItemIsDropEnabled or not flags
        self._model.hasChildren(QtCore.QModelIndex())
        self._model.hasIndex(0, 0)
        self._model.headerData(0, QtCore.Qt.Horizontal)
        self._model.index(0, 0)
        self._model.itemData(QtCore.QModelIndex())
        cache = None
        self._model.match(QtCore.QModelIndex(), -1, cache)
        self._model.mimeTypes()
        assert self._model.parent(QtCore.QModelIndex()) == QtCore.QModelIndex()
        assert self._model.rowCount() >= 0
        self._model.setData(QtCore.QModelIndex(), None, -1)
        self._model.setHeaderData(-1, QtCore.Qt.Horizontal, None)
        self._model.setHeaderData(999999, QtCore.Qt.Horizontal, None)
        self._model.sibling(0, 0, QtCore.QModelIndex())
        self._model.span(QtCore.QModelIndex())
        self._model.supportedDropActions()

    def _test_row_count(self):
        """Test model's implementation of rowCount() and hasChildren().

        Models that are dynamically populated are not as fully tested here.
        """
        # check top row
        topIndex = self._model.index(0, 0, QtCore.QModelIndex())
        rows = self._model.rowCount(topIndex)
        assert rows >= 0
        if rows > 0:
            assert self._model.hasChildren(topIndex)

        secondLevelIndex = self._model.index(0, 0, topIndex)
        if secondLevelIndex.isValid():  # not the top level
            # check a row count where parent is valid
            rows = self._model.rowCount(secondLevelIndex)
            assert rows >= 0
            if rows > 0:
                assert self._model.hasChildren(secondLevelIndex)

        # The models rowCount() is tested more extensively in
        # _check_children(), but this catches the big mistakes

    def _test_column_count(self):
        """Test model's implementation of columnCount() and hasChildren()."""

        # check top row
        topIndex = self._model.index(0, 0, QtCore.QModelIndex())
        assert self._model.columnCount(topIndex) >= 0

        # check a column count where parent is valid
        childIndex = self._model.index(0, 0, topIndex)
        if childIndex.isValid():
            assert self._model.columnCount(childIndex) >= 0

        # columnCount() is tested more extensively in _check_children(),
        # but this catches the big mistakes

    def _test_has_index(self):
        """Test model's implementation of hasIndex()."""
        # Make sure that invalid values returns an invalid index
        assert not self._model.hasIndex(-2, -2)
        assert not self._model.hasIndex(-2, 0)
        assert not self._model.hasIndex(0, -2)

        rows = self._model.rowCount()
        columns = self._model.columnCount()

        # check out of bounds
        assert not self._model.hasIndex(rows, columns)
        assert not self._model.hasIndex(rows + 1, columns + 1)

        if rows > 0:
            assert self._model.hasIndex(0, 0)

        # hasIndex() is tested more extensively in _check_children(),
        # but this catches the big mistakes

    def _test_index(self):
        """Test model's implementation of index()"""
        # Make sure that invalid values returns an invalid index
        assert self._model.index(-2, -2) == QtCore.QModelIndex()
        assert self._model.index(-2, 0) == QtCore.QModelIndex()
        assert self._model.index(0, -2) == QtCore.QModelIndex()

        rows = self._model.rowCount()
        columns = self._model.columnCount()

        if rows == 0:
            return

        # Catch off by one errors
        assert self._model.index(rows, columns) == QtCore.QModelIndex()
        assert self._model.index(0, 0).isValid()

        # Make sure that the same index is *always* returned
        a = self._model.index(0, 0)
        b = self._model.index(0, 0)
        assert a == b

        # index() is tested more extensively in _check_children(),
        # but this catches the big mistakes

    def _test_parent(self):
        """Tests model's implementation of QAbstractItemModel::parent()"""
        # Make sure the model won't crash and will return an invalid
        # QModelIndex when asked for the parent of an invalid index.
        assert self._model.parent(QtCore.QModelIndex()) == QtCore.QModelIndex()

        if self._model.rowCount() == 0:
            return

        # Column 0                | Column 1    |
        # QModelIndex()           |             |
        #    \- topIndex          | topIndex1   |
        #         \- childIndex   | childIndex1 |

        # Common error test #1, make sure that a top level index has a parent
        # that is a invalid QModelIndex.
        topIndex = self._model.index(0, 0, QtCore.QModelIndex())
        assert self._model.parent(topIndex) == QtCore.QModelIndex()

        # Common error test #2, make sure that a second level index has a
        # parent that is the first level index.
        if self._model.rowCount(topIndex) > 0:
            childIndex = self._model.index(0, 0, topIndex)
            assert self._model.parent(childIndex) == topIndex

        # Common error test #3, the second column should NOT have the same
        # children as the first column in a row.
        # Usually the second column shouldn't have children.
        topIndex1 = self._model.index(0, 1, QtCore.QModelIndex())
        if self._model.rowCount(topIndex1) > 0:
            childIndex = self._model.index(0, 0, topIndex)
            childIndex1 = self._model.index(0, 0, topIndex1)
            assert childIndex != childIndex1

        # Full test, walk n levels deep through the model making sure that all
        # parent's children correctly specify their parent.
        self._check_children(QtCore.QModelIndex())

    def _check_children(self, parent, currentDepth=0):
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
            self._fetching_more = True
            self._model.fetchMore(parent)
            self._fetching_more = False

        rows = self._model.rowCount(parent)
        columns = self._model.columnCount(parent)

        if rows > 0:
            assert self._model.hasChildren(parent)

        # Some further testing against rows(), columns(), and hasChildren()
        assert rows >= 0
        assert columns >= 0
        if rows > 0:
            assert self._model.hasChildren(parent)

        self._debug("parent:", self._model.data(parent), "rows:", rows,
                    "columns:", columns, "parent column:", parent.column())

        topLeftChild = self._model.index(0, 0, parent)

        assert not self._model.hasIndex(rows + 1, 0, parent)
        for r in range(rows):
            if self._model.canFetchMore(parent):
                self._fetching_more = True
                self._model.fetchMore(parent)
                self._fetching_more = False
            assert not self._model.hasIndex(r, columns + 1, parent)
            for c in range(columns):
                assert self._model.hasIndex(r, c, parent)
                index = self._model.index(r, c, parent)
                # rowCount() and columnCount() said that it existed...
                assert index.isValid()

                # index() should always return the same index when called twice
                # in a row
                modifiedIndex = self._model.index(r, c, parent)
                assert index == modifiedIndex

                # Make sure we get the same index if we request it twice in a
                # row
                a = self._model.index(r, c, parent)
                b = self._model.index(r, c, parent)
                assert a == b

                sibling = self._model.sibling(r, c, topLeftChild)
                assert index == sibling

                sibling = topLeftChild.sibling(r, c)
                assert index == sibling

                # Some basic checking on the index that is returned
                assert index.model() == self._orig_model
                assert index.row() == r
                assert index.column() == c
                # While you can technically return a QVariant usually this is a
                # sign of a bug in data().  Disable if this really is ok in
                # your model.
                # assert self._model.data(index, QtCore.Qt.DisplayRole).isValid()

                # If the next test fails here is some somewhat useful debug you
                # play with.

                if self._model.parent(index) != parent:
                    # FIXME
                    self._debug(r, c, currentDepth, self._model.data(index),
                                self._model.data(parent))
                    self._debug(index, parent, self._model.parent(index))
                    # And a view that you can even use to show the model.
                    # QTreeView view
                    # view.setModel(self._model)
                    # view.show()
                    pass

                # Check that we can get back our real parent.
                assert self._model.parent(index) == parent

                # recursively go down the children
                if self._model.hasChildren(index) and currentDepth < 10:
                    self._debug(r, c, "has children",
                                self._model.rowCount(index))
                    self._check_children(index, currentDepth + 1)
                # elif currentDepth >= 10:
                #     print("checked 10 deep")
                # FIXME

                # make sure that after testing the children that the index
                # doesn't change.
                newerIndex = self._model.index(r, c, parent)
                assert index == newerIndex


    def _test_data(self):
        """Test model's implementation of data()"""
        # Invalid index should return an invalid qvariant
        assert self._model.data(QtCore.QModelIndex()) == None

        if self._model.rowCount() == 0:
            return

        # A valid index should have a valid QVariant data
        assert self._model.index(0, 0).isValid()

        # shouldn't be able to set data on an invalid index
        ok = self._model.setData(QtCore.QModelIndex(), "foo",
                                 QtCore.Qt.DisplayRole)
        assert not ok

        types = [
            (QtCore.Qt.ToolTipRole, str),
            (QtCore.Qt.StatusTipRole, str),
            (QtCore.Qt.WhatsThisRole, str),
            (QtCore.Qt.SizeHintRole, QtCore.QSize),
            (QtCore.Qt.FontRole, QtGui.QFont),
            (QtCore.Qt.BackgroundColorRole, QtGui.QColor),
            (QtCore.Qt.TextColorRole, QtGui.QColor),
        ]

        # General Purpose roles that should return a QString
        for role, typ in types:
            data = self._model.data(self._model.index(0, 0), role)
            assert data == None or isinstance(data, typ), role

        # Check that the alignment is one we know about
        alignment = self._model.data(self._model.index(0, 0),
                                     QtCore.Qt.TextAlignmentRole)
        alignment = extract_from_variant(alignment)
        if alignment is not None:
            alignment = int(alignment)
            mask = int(QtCore.Qt.AlignHorizontal_Mask |
                       QtCore.Qt.AlignVertical_Mask)
            assert alignment == alignment & mask

        # Check that the "check state" is one we know about.
        state = self._model.data(self._model.index(0, 0),
                                 QtCore.Qt.CheckStateRole)
        assert state in [None, QtCore.Qt.Unchecked, QtCore.Qt.PartiallyChecked,
                         QtCore.Qt.Checked]

    def _on_rows_about_to_be_inserted(self, parent, start, end):
        """Store what is about to be inserted.

        This gets stored to make sure it actually happens in rowsInserted.
        """

        # Q_UNUSED(end)
        self._debug("rowsAboutToBeInserted", "start=", start, "end=", end, "parent=",
                    self._model.data(parent), "current count of parent=",
                    self._model.rowCount(parent), "display of last=",
                    self._model.data(self._model.index(start-1, 0, parent)))
        self._debug(self._model.index(start-1, 0, parent), self._model.data(self._model.index(start-1, 0, parent)))

        last_data = self._model.data(self._model.index(start - 1, 0, parent))
        next_data = self._model.data(self._model.index(start, 0, parent))
        c = _Changing(parent=parent, oldSize=self._model.rowCount(parent),
                      last=last_data, next=next_data)
        self._insert.append(c)

    def _on_rows_inserted(self, parent, start, end):
        """Confirm that what was said was going to happen actually did."""
        c = self._insert.pop()
        assert c.parent == parent
        self._debug("rowsInserted", "start=", start, "end=", end, "oldsize=",
                    c.oldSize, "parent=", self._model.data(parent),
                    "current rowcount of parent=", self._model.rowCount(parent))
        for ii in range(start, end):
            self._debug("itemWasInserted:", ii,
                        self._model.data(self._model.index(ii, 0, parent)))
        self._debug()

        last_data = self._model.data(self._model.index(start - 1, 0, parent))

        assert c.oldSize + (end - start + 1) == self._model.rowCount(parent)
        assert c.last == last_data

        expected = self._model.data(self._model.index(end + 1, 0, c.parent))

        if c.next != expected:
            # FIXME
            self._debug(start, end)
            for i in xrange(self._model.rowCount()):
                self._debug(self._model.index(i, 0).data())
            data = self._model.data(self._model.index(end + 1, 0, c.parent))
            self._debug(c.next, data)
            pass

        assert c.next == expected

    def _on_layout_about_to_be_changed(self):
        for i in range(max(self._model.rowCount(), 100)):
            idx = QtCore.QPersistentModelIndex(self._model.index(i, 0))
            self._changing.append(idx)

    def _on_layout_changed(self):
        for p in self._changing:
            assert p == self._model.index(p.row(), p.column(), p.parent())
        self._changing.clear()

    def _on_rows_about_to_be_removed(self, parent, start, end):
        """Store what is about to be removed to make sure it actually happens.

        This gets stored to make sure it actually happens in rowsRemoved.
        """
        last_data = self._model.data(self._model.index(start - 1, 0, parent))
        next_data = self._model.data(self._model.index(end + 1, 0, parent))
        c = _Changing(parent=parent, oldSize=self._model.rowCount(parent),
                      last=last_data, next=next_data)
        self._remove.append(c)

    def _on_rows_removed(self, parent, start, end):
        """Confirm that what was said was going to happen actually did."""
        c = self._remove.pop()
        last_data = self._model.data(self._model.index(start - 1, 0, c.parent))
        next_data = self._model.data(self._model.index(start, 0, c.parent))

        assert c.parent == parent
        assert c.oldSize - (end - start + 1) == self._model.rowCount(parent)
        assert c.last == last_data
        assert c.next == next_data

    def _on_data_changed(self, topLeft, bottomRight):
        assert topLeft.isValid()
        assert bottomRight.isValid()
        commonParent = bottomRight.parent()
        assert topLeft.parent() == commonParent
        assert topLeft.row() <= bottomRight.row()
        assert topLeft.column() <= bottomRight.column()
        rowCount = self._model.rowCount(commonParent)
        columnCount = self._model.columnCount(commonParent)
        assert bottomRight.row() < rowCount
        assert bottomRight.column() < columnCount

    def _on_header_data_changed(self, orientation, start, end):
        assert orientation in [QtCore.Qt.Horizontal, QtCore.Qt.Vertical]
        assert start >= 0
        assert end >= 0
        assert start <= end
        if orientation == QtCore.Qt.Vertical:
            itemCount = self._model.rowCount()
        else:
            itemCount = self._model.columnCount()
        assert start < itemCount
        assert end < itemCount
