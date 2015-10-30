1.9.0
-----

- Exception capturing now happens as early/late as possible in order to catch
  all possible exceptions (including fixtures)(`105`_). Thanks
  `@The-Compiler`_ for the request.

- Widgets registered by ``qtbot.addWidget`` are now closed  before all other
  fixtures are tear down (`106`_). Thanks `@The-Compiler`_ for request.

- ``qtbot`` now has a new ``wait`` method which does a blocking wait while the
  event loop continues to run, similar to ``QTest::qWait``. Thanks
  `@The-Compiler`_ for the PR (closes `107`_)!

.. _105: https://github.com/pytest-dev/pytest-qt/issues/105
.. _106: https://github.com/pytest-dev/pytest-qt/issues/106
.. _107: https://github.com/pytest-dev/pytest-qt/issues/107


1.8.0
-----

- ``pytest.mark.qt_log_ignore`` now supports an ``extend`` parameter that will extend 
  the list of regexes used to ignore Qt messages (defaults to False). 
  Thanks `@The-Compiler`_ for the PR (`99`_).

- Fixed internal error when interacting with other plugins that raise an error,
  hiding the original exception (`98`_). Thanks `@The-Compiler`_ for the PR!
  
- Now ``pytest-qt`` is properly tested with PyQt5 on Travis-CI. Many thanks
  to `@The-Compiler`_ for the PR!
  
.. _99: https://github.com/pytest-dev/pytest-qt/issues/99
.. _98: https://github.com/pytest-dev/pytest-qt/issues/98

1.7.0
-----

- ``PYTEST_QT_API`` can now be set to ``pyqt4v2`` in order to use version 2 of the 
  PyQt4 API. Thanks `@montefra`_ for the PR (`93`_)!
  
.. _93: https://github.com/pytest-dev/pytest-qt/issues/93  


1.6.0
-----

- Reduced verbosity when exceptions are captured in virtual methods
  (`77`_, thanks `@The-Compiler`_).
  
- ``pytestqt.plugin`` has been split in several files (`74`_) and tests have been
  moved out of the ``pytestqt`` package. This should not affect users, but it
  is worth mentioning nonetheless.

- ``QApplication.processEvents()`` is now called before and after other fixtures
  and teardown hooks, to better try to avoid non-processed events from leaking 
  from one test to the next. (67_, thanks `@The-Compiler`_). 

- Show Qt/PyQt/PySide versions in pytest header (68_, thanks `@The-Compiler`_!).

- Disconnect SignalBlocker functions after its loop exits to ensure second
  emissions that call the internal functions on the now-garbage-collected 
  SignalBlocker instance (#69, thanks `@The-Compiler`_ for the PR).
  
.. _77: https://github.com/pytest-dev/pytest-qt/issues/77  
.. _74: https://github.com/pytest-dev/pytest-qt/issues/74
.. _67: https://github.com/pytest-dev/pytest-qt/issues/67
.. _68: https://github.com/pytest-dev/pytest-qt/issues/68

1.5.1
-----

- Exceptions are now captured also during test tear down, as delayed events will 
  get processed then and might raise exceptions in virtual methods; 
  this is specially problematic in ``PyQt5.5``, which 
  `changed the behavior <http://pyqt.sourceforge.net/Docs/PyQt5/incompatibilities.html#pyqt-v5-5>`_ 
  to call ``abort`` by default, which will crash the interpreter. 
  (65_, thanks `@The-Compiler`_).
  
.. _65: https://github.com/pytest-dev/pytest-qt/issues/65 

1.5.0
-----

- Fixed log line number in messages, and provide better contextual information 
  in Qt5 (55_, thanks `@The-Compiler`_);
  
- Fixed issue where exceptions inside a ``waitSignals`` or ``waitSignal`` 
  with-statement block would be swallowed and a ``SignalTimeoutError`` would be 
  raised instead. (59_, thanks `@The-Compiler`_ for bringing up the issue and 
  providing a test case);
  
- Fixed issue where the first usage of ``qapp`` fixture would return ``None``. 
  Thanks to `@gqmelo`_ for noticing and providing a PR;
- New ``qtlog`` now sports a context manager method, ``disabled`` (58_). 
  Thanks `@The-Compiler`_ for the idea and testing;
  
.. _55: https://github.com/pytest-dev/pytest-qt/issues/55
.. _58: https://github.com/pytest-dev/pytest-qt/issues/58
.. _59: https://github.com/pytest-dev/pytest-qt/issues/59

1.4.0
-----

- Messages sent by ``qDebug``, ``qWarning``, ``qCritical`` are captured and displayed 
  when tests fail, similar to `pytest-catchlog`_. Also, tests 
  can be configured to automatically fail if an unexpected message is generated. 
  
- New method ``waitSignals``: will block untill **all** signals given are 
  triggered (thanks `@The-Compiler`_ for idea and complete PR).
  
- New parameter ``raising`` to ``waitSignals`` and ``waitSignals``: when ``True`` 
  will raise a ``qtbot.SignalTimeoutError`` exception when 
  timeout is reached (defaults to ``False``). 
  (thanks again to `@The-Compiler`_ for idea and complete PR).
  
- ``pytest-qt`` now requires ``pytest`` version >= 2.7.

.. _pytest-catchlog: https://pypi.python.org/pypi/pytest-catchlog

Internal changes to improve memory management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``QApplication.exit()`` is no longer called at the end of the test session 
  and the ``QApplication`` instance is not garbage collected anymore;
  
- ``QtBot`` no longer receives a QApplication as a parameter in the 
  constructor, always referencing ``QApplication.instance()`` now; this avoids 
  keeping an extra reference in the ``qtbot`` instances.
  
- ``deleteLater`` is called on widgets added in ``QtBot.addWidget`` at the end 
  of each test;
  
- ``QApplication.processEvents()`` is called at the end of each test to 
  make sure widgets are cleaned up;

1.3.0
-----

- pytest-qt now supports `PyQt5`_!

  Which Qt api will be used is still detected automatically, but you can choose 
  one using the ``PYTEST_QT_API`` environment variable 
  (the old ``PYTEST_QT_FORCE_PYQT`` is still supported for backward compatibility).

  Many thanks to `@jdreaver`_ for helping to test this release!
  
.. _PyQt5: http://pyqt.sourceforge.net/Docs/PyQt5/introduction.html  

1.2.3
-----

- Now the module ````qt_compat```` no longer sets ``QString`` and ``QVariant`` APIs to 
  ``2`` for PyQt, making it compatible for those still using version ``1`` of the 
  API.
 
1.2.2
-----

- Now it is possible to disable automatic exception capture by using markers or 
  a ``pytest.ini`` option. Consult the documentation for more information. 
  (`26`_, thanks `@datalyze-solutions`_ for bringing this up).
  
- ``QApplication`` instance is created only if it wasn't created yet 
  (`21`_, thanks `@fabioz`_!)

- ``addWidget`` now keeps a weak reference its widgets (#20, thanks `@fabioz`_)

.. _26: https://github.com/pytest-dev/pytest-qt/issues/26
.. _21: https://github.com/pytest-dev/pytest-qt/issues/21
.. _20: https://github.com/pytest-dev/pytest-qt/issues/20

1.2.1
-----

- Fixed 16_: a signal emitted immediately inside a ``waitSignal`` block now 
  works as expected (thanks `@baudren`_).

.. _16: https://github.com/pytest-dev/pytest-qt/issues/16

1.2.0
-----

This version include the new ``waitSignal`` function, which makes it easy 
to write tests for long running computations that happen in other threads 
or processes:

.. code-block:: python

    def test_long_computation(qtbot):
        app = Application()
    
        # Watch for the app.worker.finished signal, then start the worker.
        with qtbot.waitSignal(app.worker.finished, timeout=10000) as blocker:
            blocker.connect(app.worker.failed)  # Can add other signals to blocker
            app.worker.start()
            # Test will wait here until either signal is emitted, or 10 seconds has elapsed
    
        assert blocker.signal_triggered  # Assuming the work took less than 10 seconds
        assert_application_results(app)

Many thanks to `@jdreaver`_ for discussion and complete PR! (`12`_, `13`_)

.. _12: https://github.com/pytest-dev/pytest-qt/issues/12
.. _13: https://github.com/pytest-dev/pytest-qt/issues/13

1.1.1
-----

- Added ``stop`` as an alias for ``stopForInteraction`` (`10`_, thanks `@itghisi`_)

- Now exceptions raised in virtual methods make tests fail, instead of silently 
  passing (`11`_). If an exception is raised, the test will fail and it exceptions 
  that happened inside virtual calls will be printed as such::


    E           Failed: Qt exceptions in virtual methods:
    E           ________________________________________________________________________________
    E             File "x:\pytest-qt\pytestqt\_tests\test_exceptions.py", line 14, in event
    E               raise ValueError('mistakes were made')
    E
    E           ValueError: mistakes were made
    E           ________________________________________________________________________________
    E             File "x:\pytest-qt\pytestqt\_tests\test_exceptions.py", line 14, in event
    E               raise ValueError('mistakes were made')
    E
    E           ValueError: mistakes were made
    E           ________________________________________________________________________________

  Thanks to `@jdreaver`_ for request and sample code!

- Fixed documentation for ``QtBot``: it was not being rendered in the 
  docs due to an import error.

.. _10: https://github.com/pytest-dev/pytest-qt/issues/10
.. _11: https://github.com/pytest-dev/pytest-qt/issues/11

1.1.0
-----

Python 3 support.

1.0.2
-----

Minor documentation fixes.

1.0.1
-----

Small bug fix release.

1.0.0
-----

First working version.


.. _@The-Compiler: https://github.com/The-Compiler
.. _@montefra: https://github.com/montefra
.. _@gqmelo: https://github.com/gqmelo
.. _@jdreaver: https://github.com/jdreaver
.. _@datalyze-solutions: https://github.com/datalyze-solutions
.. _@fabioz: https://github.com/fabioz
.. _@baudren: https://github.com/baudren
.. _@itghisi: https://github.com/itghisi
