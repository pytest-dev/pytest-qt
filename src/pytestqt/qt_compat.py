import qtpy


from qtpy import QtTest, QtCore, QtWidgets, QtQuick, QtQml, QtGui


class qt_api:
    QtCore = QtCore
    QtTest = QtTest
    QtGui = QtGui
    QtWidgets = QtWidgets
    QtQuick = QtQuick
    QtQml = QtQml
    pytest_qt_api = qtpy.API
    qDebug = QtCore.qDebug

    @staticmethod
    def is_pyside() -> bool:
        return qtpy.API in (qtpy.PYSIDE2, qtpy.PYSIDE6)
