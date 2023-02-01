import qtpy


from qtpy import QtTest, QtCore, QtWidgets, QtQuick, QtQml, QtGui


class qt_api:
    QT_API = qtpy.API
    QtCore = QtCore
    QtTest = QtTest
    QtGui = QtGui
    QtWidgets = QtWidgets
    QtQuick = QtQuick
    QtQml = QtQml
    pytest_qt_api = qtpy.API
    Signal = QtCore.Signal

    qDebug = QtCore.qDebug
    qCritical = QtCore.qCritical
    qInfo = QtCore.qInfo
    qWarning = QtCore.qWarning
    is_pyside = qtpy.API in (qtpy.PYSIDE2, qtpy.PYSIDE6)

    is_pyqt = not is_pyside
