A note about ``pyqt4v2``
------------------------

Starting with ``pytest-qt`` version 2.0, ``PyQt`` or ``PySide`` are lazily
loaded when first needed instead of at pytest startup. This usually means
``pytest-qt`` will import ``PyQt`` or ``PySide`` when the tests actually start
running, well after ``conftest.py`` files and other plugins have been imported.
This can lead to some unexpected behaviour if ``pyqt4v2`` is set.

If the ``conftest.py`` files, either directly or indirectly, set the API version
to 2 and import ``PyQt4``, one of the following cases can happen:

* if all the available types are set to version 2, then using ``pyqt4`` or
  ``pyqt4v2`` is equivalent
* if only some of the types set to version 2, using ``pyqt4v2`` will make ``pytest``
  to fail with an error similar to::

    INTERNALERROR> sip.setapi("QDate", 2)
    INTERNALERROR> ValueError: API 'QDate' has already been set to version 1

  If this is the case, use ``pyqt4``.

If the API is set in the test functions or in the code imported by them, then
the new behaviour is indistinguishable from the old one and ``pyqt4v2`` must be
used to avoid errors if version 2 is used.
