Model Tester
============

.. versionadded:: 2.0

``pytest-qt`` includes a fixture that helps testing
`QAbstractItemModel`_ implementations. The implementation is copied
from the C++ code as described on the `Qt Wiki <http://wiki.qt.io/Model_Test>`_,
and it continuously checks a model as it changes, helping to verify the state
and catching many common errors the moment they show up.

Some of the conditions caught include:

* Verifying X number of rows have been inserted in the correct place after the signal ``rowsAboutToBeInserted()`` says X rows will be inserted.
* The parent of the first index of the first row is a ``QModelIndex()``
* Calling ``index()`` twice in a row with the same values will return the same ``QModelIndex``
* If ``rowCount()`` says there are X number of rows, model test will verify that is true.
* Many possible off by one bugs
* ``hasChildren()`` returns true if ``rowCount()`` is greater then zero.
* and many more...

To use it, create an instance of your model implementation, fill it with some
items and call ``qtmodeltester.check``:

.. code-block:: python

    def test_standard_item_model(qtmodeltester):
        model = QStandardItemModel()
        items = [QStandardItem(str(i)) for i in range(4)]
        model.setItem(0, 0, items[0])
        model.setItem(0, 1, items[1])
        model.setItem(1, 0, items[2])
        model.setItem(1, 1, items[3])
        qtmodeltester.check(model)

If the tester finds a problem the test will fail with an assert pinpointing
the issue.

The following attribute may influence the outcome of the check depending
on your model implementation:

* ``data_display_may_return_none`` (default: ``False``): While you can
  technically return ``None`` (or an invalid ``QVariant``) from ``data()``
  for ``QtCore.Qt.DisplayRole``, this usually is a sign of
  a bug in your implementation. Set this variable to ``True`` if this really
  is OK in your model.

The source code was ported from `modeltest.cpp`_ by `Florian Bruhin`_, many
thanks!

.. _modeltest.cpp: http://code.qt.io/cgit/qt/qtbase.git/tree/tests/auto/other/modeltest/modeltest.cpp

.. _Florian Bruhin: https://github.com/The-Compiler

.. _QAbstractItemModel:  http://doc.qt.io/qt-5/qabstractitemmodel.html
