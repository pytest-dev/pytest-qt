waitUntil: Waiting for arbitrary conditions
===========================================

.. versionadded:: 2.0

Sometimes your tests need to wait a certain condition which does not trigger a signal, for example
that a certain control gained focus or a ``QListView`` has been populated with all items.

For those situations you can use :meth:`qtbot.waitUntil <pytestqt.plugin.QtBot.waitUntil>` to
wait until a certain condition has been met or a timeout is reached. This is specially important
in X window systems due to their asynchronous nature, where you can't rely on the fact that the
result of an action will be immediately available.

For example:

.. code-block:: python

    def test_validate(qtbot):
        window = MyWindow()
        window.edit.setText('not a number')
        # after focusing, should update status label
        window.edit.setFocus()
        assert window.status.text() == 'Please input a number'


The ``window.edit.setFocus()`` may not be processed immediately, only in a future event loop, which
might lead to this test to work sometimes and fail in others (a *flaky* test).

A better approach in situations like this is to use ``qtbot.waitUntil`` with a callback with your
assertion:


.. code-block:: python

    def test_validate(qtbot):
        window = MyWindow()
        window.edit.setText('not a number')
        # after focusing, should update status label
        window.edit.setFocus()
        def check_label():
            assert window.status.text() == 'Please input a number'
        qtbot.waitUntil(check_label)


``qtbot.waitUntil`` will periodically call ``check_label`` until it no longer raises
``AssertionError`` or a timeout is reached. If a timeout is reached, the last assertion error
re-raised and the test will fail:

::

    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
        def check_label():
    >       assert window.status.text() == 'Please input a number'
    E       assert 'OK' == 'Please input a number'
    E         - OK
    E         + Please input a number


A second way to use ``qtbot.waitUntil`` is to pass a callback which returns ``True`` when the
condition is met or ``False`` otherwise. It is usually terser than using a separate callback with
``assert`` statement, but it produces a generic message when it fails because it can't make
use of ``pytest``'s assertion rewriting:

.. code-block:: python

    def test_validate(qtbot):
        window = MyWindow()
        window.edit.setText('not a number')
        # after focusing, should update status label
        window.edit.setFocus()
        qtbot.waitUntil(lambda: window.edit.hasFocus())
        assert window.status.text() == 'Please input a number'