import pytest
from pytestqt.qt_compat import QtGui


def test_valid_model(qtmodeltester):
    """
    Basic test which uses qtmodeltester with a QStandardItemModel.
    """
    model = QtGui.QStandardItemModel()

    items = [QtGui.QStandardItem(str(i)) for i in range(5)]

    items[0].setChild(0, items[4])
    model.setItem(0, 0, items[0])
    model.setItem(0, 1, items[1])
    model.setItem(1, 0, items[2])
    model.setItem(0, 1, items[3])

    qtmodeltester.check(model)
