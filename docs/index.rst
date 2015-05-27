.. pytest-qt documentation master file, created by
   sphinx-quickstart on Mon Mar 04 22:54:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


=========
pytest-qt
=========

:Repository: `GitHub <https://github.com/pytest-dev/pytest-qt>`_
:Version: |version|
:License: `LGPL <http://www.gnu.org/licenses/lgpl-3.0.txt>`_
:Author: Bruno Oliveira


Introduction
============

.. automodule:: pytestqt

Requirements
============

Python 2.6 or later, including Python 3+.

Tested with pytest version 2.5.2.

Works with either ``PySide``, ``PyQt4`` or ``PyQt5``, picking whichever
is available on the system giving preference to the first one installed in
this order:

- ``PySide``
- ``PyQt4``
- ``PyQt5``

To force a particular API, set the environment variable ``PYTEST_QT_API`` to
``pyside``, ``pyqt4`` or ``pyqt5``.

Installation
============

The package may be installed by running::

   pip install pytest-qt

Or alternatively, download the package from pypi_, extract and execute::

   python setup.py install

.. _pypi: http://pypi.python.org/pypi/pytest-qt/

Both methods will automatically register it for usage in ``py.test``.

Development
-----------

If you intend to develop ``pytest-qt`` itself, use virtualenv_ to
activate a new fresh environment and execute::

    git clone https://github.com/pytest-dev/pytest-qt.git
    cd pytest-qt
    python setup.py develop
    pip install pyside


.. _virtualenv: http://virtualenv.readthedocs.org/

Quick Tutorial
==============

``pytest-qt`` registers a new fixture_ named ``qtbot``, which acts as *bot* in the sense
that it can send keyboard and mouse events to any widgets being tested. This way, the programmer
can simulate user interaction while checking if GUI controls are behaving in the expected manner.

.. _fixture: http://pytest.org/latest/fixture.html

To illustrate that, consider a widget constructed to allow the user to find files in a given
directory inside an application.

.. image:: _static/find_files_dialog.png
    :align: center
    
It is a very simple dialog, where the user enters a standard file mask, optionally enters file text
to search for and a button to browse for the desired directory. Its source code is available here_,

.. _here: https://github.com/nicoddemus/PySide-Examples/blob/master/examples/dialogs/findfiles.py
     
To test this widget's basic functionality, create a test function::  

    def test_basic_search(qtbot, tmpdir):
        '''
        test to ensure basic find files functionality is working. 
        '''
        tmpdir.join('video1.avi').ensure()
        tmpdir.join('video1.srt').ensure()
        
        tmpdir.join('video2.avi').ensure()
        tmpdir.join('video2.srt').ensure()    
    
Here the first parameter indicates that we will be using a ``qtbot`` fixture to control our widget. 
The other parameter is py.test standard's tmpdir_ that we use to create some files that will be 
used during our test.    

.. _tmpdir: http://pytest.org/latest/tmpdir.html

Now we create the widget to test and register it::

    window = Window() 
    window.show()
    qtbot.addWidget(window)
    
.. tip:: Registering widgets is not required, but recommended because it will ensure those widgets get
    properly closed after each test is done.    

Now we use ``qtbot`` methods to simulate user interaction with the dialog::

    window.fileComboBox.clear()
    qtbot.keyClicks(window.fileComboBox, '*.avi')
    
    window.directoryComboBox.clear()
    qtbot.keyClicks(window.directoryComboBox, str(tmpdir))
         
The method ``keyClicks`` is used to enter text in the editable combo box, selecting the desired mask
and directory.

We then simulate a user clicking the button with the ``mouseClick`` method::
      
    qtbot.mouseClick(window.findButton, QtCore.Qt.LeftButton)
    
Once this is done, we inspect the results widget to ensure that it contains the expected files we
created earlier::

    assert window.filesTable.rowCount() == 2
    assert window.filesTable.item(0, 0).text() == 'video1.avi'
    assert window.filesTable.item(1, 0).text() == 'video2.avi'    
    


Waiting for threads, processes, etc.
====================================

.. versionadded:: 1.2

If your program has long running computations running in other threads or
processes, you can use :meth:`qtbot.waitSignal <pytestqt.plugin.QtBot.waitSignal>`
to block a test until a signal is emitted (such as ``QThread.finished``) or a
timeout is reached. This makes it easy to write tests that wait until a
computation running in another thread or process is completed before
ensuring the results are correct::

    def test_long_computation(qtbot):
        app = Application()

        # Watch for the app.worker.finished signal, then start the worker.
        with qtbot.waitSignal(app.worker.finished, timeout=10000) as blocker:
            blocker.connect(app.worker.failed)  # Can add other signals to blocker
            app.worker.start()
            # Test will block at this point until signal is emitted or
            # 10 seconds has elapsed

        assert blocker.signal_triggered, "process timed-out"
        assert_application_results(app)


.. versionadded:: 1.4

Additionally, you can pass ``raising=True`` to raise a
:class:`SignalTimeoutError` if the timeout is reached.

Exceptions in virtual methods
=============================

.. versionadded:: 1.1

It is common in Qt programming to override virtual C++ methods to customize
behavior, like listening for mouse events, implement drawing routines, etc.

Fortunately, both ``PyQt`` and ``PySide`` support overriding this virtual methods
naturally in your python code::

    class MyWidget(QWidget):

        # mouseReleaseEvent
        def mouseReleaseEvent(self, ev):
            print('mouse released at: %s' % ev.pos())

This works fine, but if python code in Qt virtual methods raise an exception
``PyQt`` and ``PySide`` will just print the exception traceback to standard
error, since this method is called deep within Qt's even loop handling and
exceptions are not allowed at that point.

This might be surprising for python users which are used to exceptions
being raised at the calling point: for example, the following code will just
print a stack trace without raising any exception::

    class MyWidget(QWidget):

        def mouseReleaseEvent(self, ev):
            raise RuntimeError('unexpected error')

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
``qt_no_exception_capture`` marker::

    @pytest.mark.qt_no_exception_capture
    def test_buttons(qtbot):
        ...

Or even disable it for your entire project in your ``pytest.ini`` file::

    [pytest]
    qt_no_exception_capture = 1

This might be desirable if you plan to install a custom exception hook.

QtBot
=====

.. module:: pytestqt.plugin
.. autoclass:: QtBot

SignalBlocker
-------------

.. autoclass:: SignalBlocker

.. autoclass:: SignalTimeoutError

Versioning
==========

This projects follows `semantic versioning`_.

.. _`semantic versioning`: http://semver.org/
