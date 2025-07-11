4.5.0 (2025-07-01)
------------------

- Added official support for Python 3.13.
- Dropped support for EOL Python 3.8.
- Dropped support for EOL PySide 2.
- Type annotations are now provided. Note that because the Qt library used is defined at runtime, Qt classes are currently annotated as ``Any``.
- Fixed PySide6 exceptions / warnings about being unable to disconnect signals
  with ``qtbot.waitSignal`` (`#552`_, `#558`_).
- Reduced the likelyhood of trouble when using ``qtbot.waitSignal(s)`` and
  ``qtbot.waitCallback`` where the signal/callback is emitted from a non-main
  thread. In theory, more problems remain and this isn't a proper fix yet. In
  practice, it seems impossible to provoke any problems in pytest-qt's testsuite.
  (`#586`_)

..  _#552: https://github.com/pytest-dev/pytest-qt/issues/552
..  _#558: https://github.com/pytest-dev/pytest-qt/issues/558
..  _#586: https://github.com/pytest-dev/pytest-qt/issues/586

4.4.0 (2024-02-07)
------------------

- ``pluggy >=1.1`` is now required: we now use new-style hook wrappers, which are less error prone.

- Fixed exception handling so they are properly cleared in Python 3.12, due to the new `sys.last_exc <https://docs.python.org/3/library/sys.html#sys.last_exc>`__ attribute (`#532`_).

..  _#532: https://github.com/pytest-dev/pytest-qt/issues/532

4.3.1 (2023-12-22)
------------------

- Added official support for Python 3.12.
- Python 3.7 is no longer supported.

- ``qapp`` now sets up the ``QApplication`` instance with a command line argument like this
  ``QApplication([prog_name])`` instead of using an empty list ``QApplication([])``.
  Here ``prog_name`` is the name of the app which defaults to ``pytest-qt-app``, but can
  be redefined in the ``pytest.ini`` file, see :ref:`qapp fixture<setting-qapp-name>`.
  Alternatively, the arguments that will be passed to ``QApplication`` can be defined
  explicitly using the ``qapp_args`` fixture. This means that the default behavior of
  the ``qapp_args`` fixture is now also changed accordingly: it now returns the list
  ``[prog_name]`` instead of an empty list. Thanks to `@The-Compiler`_ (`#483`_) and
  `@hakonhagland`_ (`#515`_).

..  _#515: https://github.com/pytest-dev/pytest-qt/pull/515
..  _#483: https://github.com/pytest-dev/pytest-qt/issues/483

4.3.0 (2023-12-22)
------------------

- Failure during publish.


4.2.0 (2022-10-25)
------------------

- Import the ``code`` sub-package from the correct location rather than the
  deprecated ``py`` package, restoring compatibility with pytest 7.2.0, where
  ``py`` was dropped. Thanks `@The-Compiler`_ for the PR.

- Use ``pytest.hookimpl`` to configure hooks, avoiding a deprecation warning in
  pytest 7.2.0. Thanks `@The-Compiler`_ for the PR.

- Now ``pytest-qt`` will check if any of the Qt libraries is already imported by the time the plugin loads,
  and use it if that is the case (`#412`_). Thanks `@eyllanesc`_ for the PR.

- Most custom ``pytest-qt`` exceptions can be accessed via ``qtbot`` (for example ``qtbot.TimeoutError``),
  but it was not always explicit in the documentation that this is the recommended way to access those exceptions, instead
  of importing them from ``pytestqt.exceptions``.
  This is now clarified in the documentation and examples, and an alias to ``ScreenshotError`` has been
  added to ``qtbot`` so it can be accessed in the same way (`#460`_).

.. _#412: https://github.com/pytest-dev/pytest-qt/pull/412
.. _#460: https://github.com/pytest-dev/pytest-qt/pull/460
.. _@eyllanesc: https://github.com/eyllanesc

4.1.0 (2022-06-23)
------------------

- ``pytest-qt`` now requires Python 3.7+.
- Improved PEP-8 aliases definition so they have a smaller call stack depth by one and better parameter suggestions in IDEs. (`#383`_). Thanks `@luziferius`_ for the PR.
- Updated model tester handling around ``hasChildren`` based on Qt's updates.
- New ``qapp_cls`` fixture returning the ``QApplication`` class to use, thus
  making it easier to use a custom subclass without having to override the
  whole ``qapp`` fixture. Thanks `@The-Compiler`_ for the PR.
- Updated model tester to track/verify in-flight changes based on Qt's updates.
  Thanks `@The-Compiler`_ for the PR.
- New ``qtbot.screenshot()`` method which can be used to take a screenshot of
  the given widget. Thanks `@The-Compiler`_ for the PR.

.. _#383: https://github.com/pytest-dev/pytest-qt/pull/383
.. _@luziferius: https://github.com/luziferius

4.0.2 (2021-06-14)
------------------

- Restored compatibility with PySide2 5.11, which doesn't depend on the
  ``shiboken2`` project, used by pytest-qt 4.0.0. The dependency is now not
  needed anymore, and the ``.isdeleted`` attribute of ``qt_compat`` (which
  isn't intended for public use) is removed.

4.0.1 (2021-06-07)
------------------

- The ``sip`` module now gets imported directly if ``PyQt5.sip`` /
  ``PyQt6.sip`` wasn't found, as it's still packaged like that in some
  distributions (`#369`_). Thanks `@The-Compiler`_ for the PR.

.. _#369: https://github.com/pytest-dev/pytest-qt/pull/369

4.0.0 (2021-06-03)
------------------

- `PySide6 <https://pypi.org/project/PySide6>`__ and `PyQt6 <https://pypi.org/project/PyQt6>`__ (6.1+)
  are now supported. Thanks `@jensheilman`_ and `@The-Compiler`_ for the PRs (`#328`_, `#330`_).
- ``pytest-qt`` now requires Python 3.6+.
- When using PyQt5, ``pytest-qt`` now requires PyQt5 5.11 or newer (`#330`_).
- Support for Qt4 (i.e. ``PyQt4`` and ``PySide``) is now dropped (`#279`_).
- The ``qtbot.waitActive`` and ``qtbot.waitExposed`` context managers are now
  available with all Qt APIs, rather than only PyQt5 (`#361`_). Thanks
  `@The-Compiler`_ for the PR.
- The ``qtbot.waitForWindowShown`` method is deprecated, as the underlying Qt
  method was obsoleted in Qt 5.0 and removed in Qt 6.0. Its name is imprecise and
  the pytest-qt wrapper does not raise TimeoutError if the window wasn't shown.
  Please use the ``qtbot.waitExposed`` context manager instead (`#361`_). Thanks
  `@The-Compiler`_ for the PR.
- The old ``qtbot.stopForInteraction()`` name is now removed as it was
  cumbersome and rarely used. Use ``qtbot.stop()`` (added in 1.1.1) instead
  (`#306`_). Thanks `@The-Compiler`_ for the PR.
- The old ``SignalTimeoutError`` exception alias is now removed, as it was renamed to
  ``TimeoutError`` in 2.1 (`#306`_). Thanks `@The-Compiler`_ for the PR.
- The old ``qt_wait_signal_raising`` option is now removed, as it was renamed to
  ``qt_default_raising`` in 3.1 (`#306`_). Thanks `@The-Compiler`_ for the PR.
- ``qtbot.waitSignal`` and ``waitSignals`` (as well as their PEP-8 aliases)
  supported passing ``None`` as signal, making them wait for the given timeout
  instead. This is not supported anymore, use ``qtbot.wait(ms)`` instead
  (`#306`_). Thanks `@The-Compiler`_ for the PR.
- Various arguments to ``qtbot`` methods are now keyword-only (`#366`_):

  * ``qtbot.waitActive``: ``timeout`` (``widget`` being the only positional argument)
  * ``qtbot.waitExposed``: ``timeout`` (``widget`` being the only positional argument)
  * ``qtbot.waitSignal``:  ``timeout``, ``raising`` and ``check_params_cb`` (``signal`` being the only positional argument)
  * ``qtbot.waitSignals``:  ``timeout``, ``raising`` and ``check_params_cbs`` (``signals`` being the only positional argument)
  * ``qtbot.assertNotEmitted``:  ``wait`` (``signal`` being the only positional argument)
  * ``qtbot.waitUntil``:  ``timeout`` (``callback`` being the only positional argument)
  * ``qtbot.waitCallback``:  ``timeout`` and ``raising`` (with no positional arguments)

  The same applies to the respective PEP-8 aliases. Thanks `@The-Compiler`_ for
  the PR.
- Various classes are now not importable from ``pytestqt.plugin`` anymore, and
  should instead be imported from the module they're residing in since the 1.6.0
  release (`#306`_):

  * ``pytestqt.plugin.QtBot`` -> ``pytestqt.qtbot.QtBot``
  * ``pytestqt.plugin.SignalBlocker`` -> ``pytestqt.wait_signal.SignalBlocker``
  * ``pytestqt.plugin.MultiSignalBlocker`` -> ``pytestqt.wait_signal.MultiSignalBlocker``
  * ``pytestqt.plugin.Record`` -> ``pytestqt.logging.Record``
  * ``pytestqt.plugin.capture_exceptions`` ->
    ``pytestqt.exceptions.capture_exceptions`` (but consider using
    ``qtbot.capture_exceptions`` instead)
  * ``pytestqt.plugin.format_captured_exceptions`` ->
    ``pytestqt.exceptions.format_captured_exceptions``
- The ``qt_api.extract_from_variant`` and ``qt_api.make_variant`` functions
  (which were never intended for public usage) as well as all class aliases
  (such as ``qt_api.QWidget`` or ``qt_api.QEvent``, among others) are now
  removed. Thanks `@The-Compiler`_ for the PR.
- The default timeouts for ``qtbot.waitSignal``, ``waitSignals``, ``waitUntil``
  and ``waitCallback``, ``waitActive`` and ``waitExposed`` have been raised from
  1s to 5s. This makes them in line the default timeout used by Qt's underlying
  methods such as ``QSignalSpy::wait``. To get the old behavior back, explicitly
  pass ``timeout=1000`` to those functions (`#306`_). Thanks `@The-Compiler`_
  for the PR.
- ``waitUntil`` now raises a ``TimeoutError`` when a timeout occurs to make the
  cause of the timeout more explicit (`#222`_). Thanks `@karlch`_ for the PR.
- The ``QtTest::keySequence`` method is now exposed (if available, with Qt >=
  5.10) (`#289`_). Thanks `@The-Compiler`_ for the PR.
- ``addWidget`` now enforces that its argument is a ``QWidget`` in order to
  display a clearer error when this isn't the case (`#290`_). Thanks
  `@The-Compiler`_ for the PR.
- New option ``qt_qapp_name`` can be used to set the name of the
  ``QApplication`` created by ``pytest-qt``, defaulting to ``"pytest-qt-qapp"``
  (`#302`_). Thanks `@The-Compiler`_ for the PR.
- When the ``-s`` (``--capture=no``) argument is passed to pytest, Qt log
  capturing is now disabled as well (`#300`_). Thanks `@The-Compiler`_ for the PR.
- PEP-8 aliases (``add_widget``, ``wait_active``, etc) are no longer just simple
  assignments to the methods, but they are real methods which call the normal
  implementations. This makes subclasses work as expected, instead of having to
  duplicate the assignment (`#326`_, `#333`_). Thanks `@oliveira-mauricio`_ and
  `@jensheilman`_ for the PRs.
- Errors related to the ``qt_compat`` module (such as an invalid
  ``PYTEST_QT_API`` setting or missing Qt API wrappers) are now shown as a more
  human-readable error message rather than an internal pytest error (`#355`_). Thanks
  `@The-Compiler`_ for the PR.

.. _#222: https://github.com/pytest-dev/pytest-qt/pull/222
.. _#326: https://github.com/pytest-dev/pytest-qt/pull/326
.. _#328: https://github.com/pytest-dev/pytest-qt/issues/328
.. _#330: https://github.com/pytest-dev/pytest-qt/pull/330
.. _#279: https://github.com/pytest-dev/pytest-qt/pull/279
.. _#361: https://github.com/pytest-dev/pytest-qt/pull/361
.. _#306: https://github.com/pytest-dev/pytest-qt/pull/306
.. _#289: https://github.com/pytest-dev/pytest-qt/pull/289
.. _#290: https://github.com/pytest-dev/pytest-qt/issues/290
.. _#302: https://github.com/pytest-dev/pytest-qt/pull/302
.. _#300: https://github.com/pytest-dev/pytest-qt/pull/300
.. _#333: https://github.com/pytest-dev/pytest-qt/issue/333
.. _#355: https://github.com/pytest-dev/pytest-qt/issue/355
.. _#366: https://github.com/pytest-dev/pytest-qt/issue/366
.. _@karlch: https://github.com/karlch
.. _@oliveira-mauricio: https://github.com/oliveira-mauricio
.. _@jensheilman: https://github.com/jensheilman

3.3.0 (2019-12-07)
------------------

- Improve message in uncaught exceptions by mentioning the Qt event loop instead of
  Qt virtual methods (`#255`_).

- ``pytest-qt`` now requires ``pytest`` version >= 3.0.

- ``qtbot.addWiget`` now supports an optional ``before_close_func`` keyword-only argument, which if given is a function
  which is called before the widget is closed, with the widget as first argument.

.. _#255: https://github.com/pytest-dev/pytest-qt/pull/255

3.2.2 (2018-12-13)
------------------

- Fix Off-by-one error in ``modeltester`` (`#249`_). Thanks `@ext-jmmugnes`_ for the PR.

.. _#249: https://github.com/pytest-dev/pytest-qt/pull/249


3.2.1 (2018-10-01)
------------------

- Fixed compatibility with PyQt5 5.11.3

3.2.0 (2018-09-26)
------------------

- The ``CallbackBlocker`` returned by ``qtbot.waitCallback()`` now has a new
  ``assert_called_with(...)`` convenience method.

3.1.0 (2018-09-23)
------------------

- If Qt's model tester implemented in C++ is available (PyQt5 5.11 or newer),
  the ``qtmodeltester`` fixture now uses that instead of the Python
  implementation. This can be turned off by passing  ``force_py=True`` to
  ``qtmodeltester.check()``.

- The Python code used by ``qtmodeltester`` is now based on the latest Qt
  modeltester. This also means that the ``data_display_may_return_none``
  attribute for ``qtmodeltester`` isn't used anymore.

- New ``qtbot.waitCallback()`` method that returns a ``CallbackBlocker``, which
  can be used to wait for a callback to be called.

- ``qtbot.assertNotEmitted`` now has a new ``wait`` parameter which can be used
  to make sure asynchronous signals aren't emitted by waiting after the code in
  the ``with`` block finished.

- The ``qt_wait_signal_raising`` option was renamed to ``qt_default_raising``.
  The old name continues to work, but is deprecated.

- The docs still referred to ``SignalTimeoutError`` in some places, despite it
  being renamed to ``TimeoutError`` in the 2.1 release. This is now corrected.

- Improve debugging output when no Qt wrapper was found.

- When no context is available for warnings on Qt 5, no ``None:None:0`` line is
  shown anymore.

- The ``no_qt_log`` marker is now registered with pytest so ``--strict`` can be
  used.

- ``qtbot.waitSignal`` with timeout ``0`` now expects the signal to arrive
  directly in the code enclosed by it.

Thanks `@The-Compiler`_ for the PRs.

3.0.2 (2018-08-31)
------------------

- Another fix related to ``QtInfoMsg`` objects during logging (`#225`_).


3.0.1 (2018-08-30)
------------------

- Fix handling of ``QtInfoMsg`` objects during logging (`#225`_).
  Thanks `@willsALMANJ`_ for the report.

.. _#225: https://github.com/pytest-dev/pytest-qt/issues/225


3.0.0 (2018-07-12)
------------------

- Removed ``qtbot.mouseEvent`` proxy, it was an internal Qt function which has
  now been removed in PyQt 5.11 (`#219`_). Thanks `@mitya57`_ for the PR.

- Fix memory leak when tests raised an exception inside Qt virtual methods (`#187`_).
  Thanks `@fabioz`_ for the report and PR.

.. _#187: https://github.com/pytest-dev/pytest-qt/issues/187
.. _#219: https://github.com/pytest-dev/pytest-qt/pull/219


2.4.1 (2018-06-14)
------------------

- Properly handle chained exceptions when capturing them inside
  virtual methods (`#215`_). Thanks `@fabioz`_ for the report and sample
  code with the fix.

.. _#215: https://github.com/pytest-dev/pytest-qt/pull/215


2.4.0
-----

- Use new pytest 3.6 marker API when possible (`#212`_). Thanks `@The-Compiler`_ for the PR.

.. _#212: https://github.com/pytest-dev/pytest-qt/pull/212

2.3.2
-----

- Fix ``QStringListModel`` import when using ``PySide2`` (`#209`_). Thanks `@rth`_ for the PR.

.. _#209: https://github.com/pytest-dev/pytest-qt/pull/209


2.3.1
-----

- ``PYTEST_QT_API`` environment variable correctly wins over ``qt_api``
  ini variable if both are set at the same time (`#196`_). Thanks `@mochick`_ for the PR.

.. _#196: https://github.com/pytest-dev/pytest-qt/pull/196


2.3.0
-----

- New ``qapp_args`` fixture which can be used to pass custom arguments to
  ``QApplication``.
  Thanks `@The-Compiler`_ for the PR.

2.2.1
-----

- ``modeltester`` now accepts ``QBrush`` for ``BackgroundColorRole`` and ``TextColorRole`` (`#189`_).
  Thanks `@p0las`_ for the PR.

.. _#189: https://github.com/pytest-dev/pytest-qt/issues/189



2.2.0
-----

- ``pytest-qt`` now supports `PySide2`_ thanks to `@rth`_!

.. _PySide2: https://wiki.qt.io/PySide2


2.1.2
-----

- Fix issue where ``pytestqt`` was hiding the information when there's an exception raised from another exception on Python 3.

2.1.1
-----

- Fixed tests on Python 3.6.

2.1
---

- ``waitSignal`` and ``waitSignals`` now provide much more detailed messages
  when expected signals are not emitted. Many thanks to `@MShekow`_ for the PR
  (`#153`_).

- ``qtbot`` fixture now can capture Qt virtual method exceptions in a block using
  ``captureExceptions`` (`#154`_). Thanks to `@fogo`_ for the PR.

- New `qtbot.waitActive`_ and `qtbot.waitExposed`_ methods for PyQt5.
  Thanks `@The-Compiler`_ for the request (`#158`_).

- ``SignalTimeoutError`` has been renamed to ``TimeoutError``. ``SignalTimeoutError`` is kept as
  a backward compatibility alias.

.. _qtbot.waitActive: http://pytest-qt.readthedocs.io/en/latest/reference.html#pytestqt.qtbot.QtBot.waitActive
.. _qtbot.waitExposed: http://pytest-qt.readthedocs.io/en/latest/reference.html#pytestqt.qtbot.QtBot.waitExposed

.. _#153: https://github.com/pytest-dev/pytest-qt/issues/153
.. _#154: https://github.com/pytest-dev/pytest-qt/issues/154
.. _#158: https://github.com/pytest-dev/pytest-qt/issues/158

2.0
---

Breaking Changes
~~~~~~~~~~~~~~~~

With ``pytest-qt`` 2.0, we changed some defaults to values we think are much
better, however this required some backwards-incompatible changes:

- ``pytest-qt`` now defaults to using ``PyQt5`` if ``PYTEST_QT_API`` is not set.
  Before, it preferred ``PySide`` which is using the discontinued Qt4.

- Python 3 versions prior to 3.4 are no longer supported.

- The ``@pytest.mark.qt_log_ignore`` mark now defaults to ``extend=True``, i.e.
  extends the patterns defined in the config file rather than overriding them.
  You can pass ``extend=False`` to get the old behaviour of overriding the
  patterns.

- ``qtbot.waitSignal`` now defaults to ``raising=True`` and raises an exception
  on timeouts. You can set ``qt_wait_signal_raising = false`` in your config to
  get back the old behaviour.

- ``PYTEST_QT_FORCE_PYQT`` environment variable is no longer supported. Set ``PYTEST_QT_API``
  to the appropriate value instead or the new ``qt_api`` configuration option in your
  ``pytest.ini`` file.


New Features
~~~~~~~~~~~~

* From this version onward, ``pytest-qt`` is licensed under the MIT license (`#134`_).

* New ``qtmodeltester`` fixture to test ``QAbstractItemModel`` subclasses.
  Thanks `@The-Compiler`_ for the initiative and port of the original C++ code
  for ModelTester (`#63`_).

* New ``qtbot.waitUntil`` method, which continuously calls a callback until a condition
  is met or a timeout is reached. Useful for testing asynchronous features
  (like in X window environments for example).

* ``waitSignal`` and ``waitSignals`` can receive an optional callback (or list of callbacks)
  that can evaluate if the arguments of emitted signals should resume execution or not.
  Additionally ``waitSignals`` has a new ``order`` parameter that allows to expect signals
  and their arguments in a strict, semi-strict or no specific order.
  Thanks `@MShekow`_ for the PR (`#141`_).

* Now which Qt binding ``pytest-qt`` will use can be configured by the ``qt_api`` config option.
  Thanks `@The-Compiler`_ for the request (`#129`_).

* While ``pytestqt.qt_compat`` is an internal module and shouldn't be imported directly,
  it is known that some test suites did import it. This module now uses a lazy-load mechanism
  to load Qt classes and objects, so the old symbols (``QtCore``, ``QApplication``, etc.) are
  no longer available from it.

.. _#134: https://github.com/pytest-dev/pytest-qt/issues/134
.. _#141: https://github.com/pytest-dev/pytest-qt/pull/141
.. _#63: https://github.com/pytest-dev/pytest-qt/pull/63
.. _#129: https://github.com/pytest-dev/pytest-qt/issues/129


Other Changes
~~~~~~~~~~~~~

- Exceptions caught by ``pytest-qt`` in ``sys.excepthook`` are now also printed
  to ``stderr``, making debugging them easier from within an IDE.
  Thanks `@fabioz`_ for the PR (`126`_)!

.. _126: https://github.com/pytest-dev/pytest-qt/pull/126

1.11.0
------

.. note::

    The default value for ``raising`` is planned to change to ``True`` starting in
    pytest-qt version ``1.12``. Users wishing to preserve
    the current behavior (``raising`` is ``False`` by default) should make
    use of the new ``qt_wait_signal_raising`` ini option below.

- New ``qt_wait_signal_raising`` ini option can be used to override the default
  value of the ``raising`` parameter of the ``qtbot.waitSignal`` and
  ``qtbot.waitSignals`` functions when omitted:

  .. code-block:: ini

      [pytest]
      qt_wait_signal_raising = true

  Calls which explicitly pass the ``raising`` parameter are not affected.
  Thanks `@The-Compiler`_ for idea and initial work on a PR (`120`_).


- ``qtbot`` now has a new ``assertNotEmitted`` context manager which can be
  used to ensure the given signal is not emitted (`92`_).
  Thanks `@The-Compiler`_ for the PR!


.. _92: https://github.com/pytest-dev/pytest-qt/issues/92
.. _120: https://github.com/pytest-dev/pytest-qt/issues/120


1.10.0
------

- ``SignalBlocker`` now has a ``args`` attribute with the arguments of the
  signal that triggered it, or ``None`` on a time out (`115`_).
  Thanks `@billyshambrook`_ for the request and `@The-Compiler`_ for the PR.

- ``MultiSignalBlocker`` is now properly disconnects from signals upon exit.

.. _115: https://github.com/pytest-dev/pytest-qt/issues/115

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

- raise ``RuntimeError`` instead of ``ImportError`` when failing to import
  any Qt binding: raising the latter causes ``pluggy`` in ``pytest-2.8`` to
  generate a subtle warning instead of a full blown error.
  Thanks `@Sheeo`_ for bringing this problem to attention (closes `109`_).

.. _105: https://github.com/pytest-dev/pytest-qt/issues/105
.. _106: https://github.com/pytest-dev/pytest-qt/issues/106
.. _107: https://github.com/pytest-dev/pytest-qt/issues/107
.. _109: https://github.com/pytest-dev/pytest-qt/issues/109


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

- New method ``waitSignals``: will block until **all** signals given are
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

- ``addWidget`` now keeps a weak reference its widgets (`20`_, thanks `@fabioz`_)

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


.. _@baudren: https://github.com/baudren
.. _@billyshambrook: https://github.com/billyshambrook
.. _@datalyze-solutions: https://github.com/datalyze-solutions
.. _@ext-jmmugnes: https://github.com/ext-jmmugnes
.. _@fabioz: https://github.com/fabioz
.. _@fogo: https://github.com/fogo
.. _@gqmelo: https://github.com/gqmelo
.. _@hakonhagland: https://github.com/hakonhagland
.. _@itghisi: https://github.com/itghisi
.. _@jdreaver: https://github.com/jdreaver
.. _@mitya57: https://github.com/mitya57
.. _@mochick: https://github.com/mochick
.. _@montefra: https://github.com/montefra
.. _@MShekow: https://github.com/MShekow
.. _@p0las: https://github.com/p0las
.. _@rth: https://github.com/rth
.. _@Sheeo: https://github.com/Sheeo
.. _@The-Compiler: https://github.com/The-Compiler
.. _@willsALMANJ: https://github.com/willsALMANJ
