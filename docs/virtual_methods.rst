Exceptions in virtual methods
=============================

.. versionadded:: 1.1

It is common in Qt programming to override virtual C++ methods to customize
behavior, like listening for mouse events, implement drawing routines, etc.

Fortunately, all Python bindings for Qt support overriding these virtual methods
naturally in your Python code:

.. code-block:: python

    class MyWidget(QWidget):
        # mouseReleaseEvent
        def mouseReleaseEvent(self, ev):
            print(f"mouse released at: {ev.pos()}")

In ``PyQt5`` and ``PyQt6``, exceptions in virtual methods will by default call
abort(), which will crash the interpreter. All other Qt wrappers will print the
exception stacktrace and return a default value back to C++/Qt (if a return
value is required).

This might be surprising for Python users which are used to exceptions
being raised at the calling point: For example, the following code will just
print a stack trace without raising any exception:

.. code-block:: python

    class MyWidget(QWidget):
        def mouseReleaseEvent(self, ev):
            raise RuntimeError("unexpected error")


    w = MyWidget()
    QTest.mouseClick(w, QtCore.Qt.LeftButton)


To make testing Qt code less surprising, ``pytest-qt`` automatically
installs an exception hook which captures errors and fails tests when exceptions
are raised inside virtual methods, like this::

    E           Failed: Qt exceptions in virtual methods:
    E           ________________________________________________________________________________
    E             File "x:\pytest-qt\pytestqt\_tests\test_exceptions.py", line 14, in event
    E               raise RuntimeError('unexpected error')
    E
    E           RuntimeError: unexpected error


Disabling the automatic exception hook
--------------------------------------

You can disable the automatic exception hook on individual tests by using a
``qt_no_exception_capture`` marker:

.. code-block:: python

    @pytest.mark.qt_no_exception_capture
    def test_buttons(qtbot):
        ...

Or even disable it for your entire project in your ``pytest.ini`` file:

.. code-block:: ini

    [pytest]
    qt_no_exception_capture = 1

This might be desirable if you plan to install a custom exception hook.


.. note::

    Starting with ``PyQt5.5``, exceptions raised during virtual methods will
    actually trigger an ``abort()``, crashing the Python interpreter. For this
    reason, disabling exception capture in ``PyQt5.5+`` and ``PyQt6`` is not
    recommended unless you install your own exception hook.
