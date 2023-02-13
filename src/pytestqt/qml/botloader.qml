import QtQuick 2.15
import QtQuick.Window 2.15

Window {
    id: root
    width: 500
    height: 400
    visible: true


    Item {
        anchors.fill: parent
        Loader {
            objectName: "contentloader"
            source: ""
        }
    }
}
