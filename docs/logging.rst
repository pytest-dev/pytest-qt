Qt Logging Capture
==================

.. versionadded:: 1.4

Qt features its own logging mechanism through ``qInstallMessageHandler``
(``qInstallMsgHandler`` on Qt4) and ``qDebug``, ``qWarning``, ``qCritical``
functions. These are used by Qt to print warning messages when internal errors
occur.

``pytest-qt`` automatically captures these messages and displays them when a
test fails, similar to what ``pytest`` does for ``stderr``  and ``stdout`` and
the `pytest-catchlog <https://github.com/eisensheng/pytest-catchlog>`_ plugin.
For example:

.. code-block:: python

    from pytestqt.qt_compat import qWarning

    def do_something():
        qWarning('this is a WARNING message')

    def test_foo():
        do_something()
        assert 0


.. code-block:: bash

    $ py.test test.py -q
    F
    ================================== FAILURES ===================================
    _________________________________ test_types __________________________________

        def test_foo():
            do_something()
    >       assert 0
    E       assert 0

    test.py:8: AssertionError
    ---------------------------- Captured Qt messages -----------------------------
    QtWarningMsg: this is a WARNING message
    1 failed in 0.01 seconds


Disabling Logging Capture
-------------------------

Qt logging capture can be disabled altogether by passing the ``--no-qt-log``
to the command line, which will fallback to the default Qt bahavior of printing
emitted messages directly to ``stderr``:

.. code-block:: bash

    py.test test.py -q --no-qt-log
    F
    ================================== FAILURES ===================================
    _________________________________ test_types __________________________________

        def test_foo():
            do_something()
    >       assert 0
    E       assert 0

    test.py:8: AssertionError
    ---------------------------- Captured stderr call -----------------------------
    this is a WARNING message


qtlog fixture
-------------


``pytest-qt`` also provides a ``qtlog`` fixture that can used
to check if certain messages were emitted during a test::

    def do_something():
        qWarning('this is a WARNING message')

    def test_foo(qtlog):
        do_something()
        emitted = [(m.type, m.message.strip()) for m in qtlog.records]
        assert emitted == [(QtWarningMsg, 'this is a WARNING message')]


``qtlog.records`` is a list of :class:`Record <pytestqt.plugin.Record>`
instances.

Logging can also be disabled on a block of code using the ``qtlog.disabled()``
context manager, or with the ``pytest.mark.no_qt_log`` mark:

.. code-block:: python

    def test_foo(qtlog):
        with qtlog.disabled():
            # logging is disabled within the context manager
            do_something()

    @pytest.mark.no_qt_log
    def test_bar():
        # logging is disabled for the entire test
        do_something()


Keep in mind that when logging is disabled,
``qtlog.records`` will always be an empty list.

Log Formatting
--------------

The output format of the messages can also be controlled by using the
``--qt-log-format`` command line option, which accepts a string with standard
``{}`` formatting which can make use of attribute interpolation of the record
objects:

.. code-block:: bash

    $ py.test test.py --qt-log-format="{rec.when} {rec.type_name}: {rec.message}"

Keep in mind that you can make any of the options above the default
for your project by using pytest's standard ``addopts`` option in you
``pytest.ini`` file:


.. code-block:: ini

    [pytest]
    qt_log_format = {rec.when} {rec.type_name}: {rec.message}


Automatically failing tests when logging messages are emitted
-------------------------------------------------------------

Printing messages to ``stderr`` is not the best solution to notice that
something might not be working as expected, specially when running in a
continuous integration server where errors in logs are rarely noticed.

You can configure ``pytest-qt`` to automatically fail a test if it emits
a message of a certain level or above using the ``qt_log_level_fail`` ini
option:


.. code-block:: ini

    [pytest]
    qt_log_level_fail = CRITICAL

With this configuration, any test which emits a CRITICAL message or above
will fail, even if no actual asserts fail within the test:

.. code-block:: python

    from pytestqt.qt_compat import qCritical

    def do_something():
        qCritical('WM_PAINT failed')

    def test_foo(qtlog):
        do_something()


.. code-block:: bash

    >py.test test.py --color=no -q
    F
    ================================== FAILURES ===================================
    __________________________________ test_foo ___________________________________
    test.py:5: Failure: Qt messages with level CRITICAL or above emitted
    ---------------------------- Captured Qt messages -----------------------------
    QtCriticalMsg: WM_PAINT failed

The possible values for ``qt_log_level_fail`` are:

* ``NO``: disables test failure by log messages.
* ``DEBUG``: messages emitted by ``qDebug`` function or above.
* ``WARNING``: messages emitted by ``qWarning`` function or above.
* ``CRITICAL``: messages emitted by ``qCritical`` function only.

If some failures are known to happen and considered harmless, they can
be ignored by using the ``qt_log_ignore`` ini option, which
is a list of regular expressions matched using ``re.search``:

.. code-block:: ini

    [pytest]
    qt_log_level_fail = CRITICAL
    qt_log_ignore =
        WM_DESTROY.*sent
        WM_PAINT failed

.. code-block:: bash

    py.test test.py --color=no -q
    .
    1 passed in 0.01 seconds


Messages which do not match any of the regular expressions
defined by ``qt_log_ignore`` make tests fail as usual:

.. code-block:: python

    def do_something():
        qCritical('WM_PAINT not handled')
        qCritical('QObject: widget destroyed in another thread')

    def test_foo(qtlog):
        do_something()

.. code-block:: bash

    py.test test.py --color=no -q
    F
    ================================== FAILURES ===================================
    __________________________________ test_foo ___________________________________
    test.py:6: Failure: Qt messages with level CRITICAL or above emitted
    ---------------------------- Captured Qt messages -----------------------------
    QtCriticalMsg: WM_PAINT not handled  (IGNORED)
    QtCriticalMsg: QObject: widget destroyed in another thread


You can also override the ``qt_log_level_fail`` setting and extend
``qt_log_ignore`` patterns from ``pytest.ini`` in some tests by using a mark
with the same name:

.. code-block:: python

    def do_something():
        qCritical('WM_PAINT not handled')
        qCritical('QObject: widget destroyed in another thread')

    @pytest.mark.qt_log_level_fail('CRITICAL')
    @pytest.mark.qt_log_ignore('WM_DESTROY.*sent', 'WM_PAINT failed')
    def test_foo(qtlog):
        do_something()

If you would like to override the list of ignored patterns instead, pass
``extend=False`` to the ``qt_log_ignore`` mark:

.. code-block:: python

    @pytest.mark.qt_log_ignore('WM_DESTROY.*sent', extend=False)
    def test_foo(qtlog):
        do_something()
