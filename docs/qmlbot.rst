=========
qmlbot
=========

Fixture that helps interacting with QML.

Example - load qml from string:
.. code-block:: python

    def test_say_hello(qmlbot):
        qml = """
        import QtQuick 2.0

        Rectangle{
            objectName: "sample";
            property string hello: "world"
        }
        """
        item = qmlbot.loads(qml)
        assert item.property("hello") == "world"

Example - load qml from file

.. code-block:: python
    from pathlib import Path


    def test_say_hello(qmlbot):
        item = qmlbot.load(Path("sayhello.qml"))
        assert item.property("hello") == "world"

Note: if your components depends on any instances or ``@QmlElement``'s you need
to make sure it is acknowledge by ``qmlbot.engine``
