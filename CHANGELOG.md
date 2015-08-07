# 1.6.0.dev #

# 1.5.2.dev #

- Show Qt/PyQt/PySide versions in pytest header (#68, thanks @The-Compiler!).

- Disconnect SignalBlocker functions after its loop exits to ensure second
  emissions to call the internal functions on the now-garbage-collected 
  SignalBlocker instance (#69, thanks @The-Compiler for the PR).

# 1.5.1 #

* Exceptions are now captured also during test tear down, as delayed events will 
  get processed then and might raise exceptions in virtual methods; 
  this is specially problematic in `PyQt5.5`, which 
  [changed the behavior](http://pyqt.sourceforge.net/Docs/PyQt5/incompatibilities.html#pyqt-v5-5) 
  to call `abort` by default, which will crash the interpreter. 
  (#65, thanks @The-Compiler).

# 1.5.0 #

- Fixed log line number in messages, and provide better contextual information 
  in Qt5 (#55, thanks @The-Compiler);
  
- Fixed issue where exceptions inside a `waitSignals` or `waitSignal` 
  with-statement block would be swallowed and a `SignalTimeoutError` would be 
  raised instead. (#59, thanks @The-Compiler for bringing up the issue and 
  providing a test case);
  
- Fixed issue where the first usage of `qapp` fixture would return `None`. 
  Thanks to @gqmelo for noticing and providing a PR;
- New `qtlog` now sports a context manager method, `disabled` (#58). 
  Thanks @The-Compiler for the idea and testing;

# 1.4.0 #

- Messages sent by `qDebug`, `qWarning`, `qCritical` are captured and displayed 
  when tests fail, similar to 
  [pytest-catchlog](https://pypi.python.org/pypi/pytest-catchlog). Also, tests 
  can be configured to automatically fail if an unexpected message is generated. 
  (See [docs](http://pytest-qt.readthedocs.org/en/latest/logging.html)).
  
- New method `waitSignals`: will block untill **all** signals given are 
  triggered, see [docs](http://pytest-qt.readthedocs.org/en/master/signals.html)
  (thanks @The-Compiler for idea and  complete PR).
- New parameter `raising` to `waitSignals` and `waitSignals`: when `True` 
  (defaults to `False`) will raise a `qtbot.SignalTimeoutError` exception when 
  timeout is reached, see 
  [docs](http://pytest-qt.readthedocs.org/en/master/signals.html) 
  (thanks again to @The-Compiler for idea and complete PR).
  
- `pytest-qt` now requires `pytest` version >= 2.7.

## Internal changes to improve memory management ##

- `QApplication.exit()` is no longer called at the end of the test session 
  and the `QApplication` instance is not garbage collected anymore;
- `QtBot` no longer receives a QApplication as a parameter in the 
  constructor, always referencing `QApplication.instance()` now; this avoids 
  keeping an extra reference in the `qtbot` instances.
- `deleteLater` is called on widgets added in `QtBot.addWidget` at the end 
  of each test;
  
- `QApplication.processEvents()` is called at the end of each test to 
  make sure widgets are cleaned up;

# 1.3.0 #

- pytest-qt now supports [PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/introduction.html)!

  Which Qt api will be used is still detected automatically, but you can choose one using the `PYTEST_QT_API` environment variable (the old `PYTEST_QT_FORCE_PYQT` is still supported for backward compatibility).

  Many thanks to @jdreaver for helping to test this release!

# 1.2.3 #

- Now the module `qt_compat` no longer sets `QString` and `QVariant` APIs to 
  `2` for PyQt, making it compatible for those still using version `1` of the 
  API.
 
# 1.2.2 #

- Now it is possible to disable automatic exception capture by using markers or 
  a `pytest.ini` option. Consult the documentation for more information. 
  (#26, thanks @datalyze-solutions for bringing this up).
  
- `QApplication` instance is created only if it wasn't created yet 
  (#21, thanks @fabioz!)

- `addWidget` now keeps a weak reference its widgets (#20, thanks @fabioz)

# 1.2.1 #

- Fixed #16: a signal emitted immediately inside a `waitSignal` block now 
works as expected (thanks @baudren)

# 1.2.0 #

This version include the new `waitSignal` function, which makes it easy 
to write tests for long running computations that happen in other threads 
or processes:

```python
def test_long_computation(qtbot):
    app = Application()

    # Watch for the app.worker.finished signal, then start the worker.
    with qtbot.waitSignal(app.worker.finished, timeout=10000) as blocker:
        blocker.connect(app.worker.failed)  # Can add other signals to blocker
        app.worker.start()
        # Test will wait here until either signal is emitted, or 10 seconds has elapsed

    assert blocker.signal_triggered  # Assuming the work took less than 10 seconds
    assert_application_results(app)
``` 

Many thanks to @jdreaver for discussion and complete PR! (#12, #13)

# 1.1.1 #

- Added `stop` as an alias for `stopForInteraction` (#10, thanks @itghisi)

- Now exceptions raised in virtual methods make tests fail, instead of silently 
passing (#11). If an exception is raised, the test will fail and it exceptions 
that happened inside virtual calls will be printed as such:

```
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
```

  Thanks to @jdreaver for request and sample code!

- Fixed documentation for `QtBot`: it was not being rendered in the 
  docs due to an import error.

# 1.1.0 #

Python 3 support.

# 1.0.2 #

Minor documentation fixes.

# 1.0.1 #

Small bug fix release.

# 1.0.0 #

First working version.