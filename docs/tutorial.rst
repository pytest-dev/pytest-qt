Tutorial
========

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

To test this widget's basic functionality, create a test function:

.. code-block:: python

    def test_basic_search(qtbot, tmp_path):
        """
        test to ensure basic find files functionality is working.
        """
        tmp_path.joinpath("video1.avi").touch()
        tmp_path.joinpath("video1.srt").touch()

        tmp_path.joinpath("video2.avi").touch()
        tmp_path.joinpath("video2.srt").touch()

Here the first parameter indicates that we will be using a ``qtbot`` fixture to control our widget.

.. note::

    It is not necessary to create a QApplication instance, since the ``qtbot`` fixture will
    do this for you. The ``QApplication`` object is accessible through the
    ``QApplication.instance()``_ function that returns a pointer equivalent to the global
    ``qApp`` pointer.

The other parameter is pytest's standard tmpdir_ that we use to create some files that will be
used during our test.

.. _QApplication.instance(): https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QApplication.html
.. _tmpdir: http://pytest.org/latest/tmpdir.html

Now we create the widget to test and register it:

.. code-block:: python

    window = Window()
    window.show()
    qtbot.addWidget(window)

.. tip:: Registering widgets is not required, but recommended because it will ensure those widgets get
    properly closed after each test is done.

Now we can interact with the widgets directly:

.. code-block:: python

    window.fileComboBox.clear()
    window.fileComboBox.setCurrentText("*.avi")

    window.directoryComboBox.clear()
    window.directoryComboBox.setCurrentText(str(tmp_path))


We use the ``QComboBox.setCurrentText`` method to change the current item selected in the combo box.


.. _note-about-qtbot-methods:

.. note::

    In general, prefer to use a widget's own methods to interact with it: ``QComboBox.setCurrentIndex``, ``QLineEdit.setText``,
    etc. Those methods will emit the appropriate signal, so the test will work just the same as if the user themselves
    have interacted with the controls.

    Note that ``qtbot`` provides a number of methods to simulate actual interaction, for example ``keyClicks``, ``mouseClick``,
    etc. Those methods should be used only in specialized situations, for example if you are creating a custom drawing widget
    and want to simulate actual clicks.

    For normal interactions, always prefer widget methods (``setCurrentIndex``, ``setText``, etc) -- ``qtbot``'s methods
    (``keyClicks``, ``mouseClick``, etc) will trigger an actual event, which will then need to be processed in the next
    pass of the event loop, making the test unreliable and flaky. Also some operations are hard to simulate using
    raw clicks, for example selecting an item on a ``QComboBox``, which will need two ``mouseClick``
    calls to simulate properly, while figuring out where to click.


We then simulate a user clicking the button:

.. code-block:: python

    window.findButton.click()

Once this is done, we inspect the results widget to ensure that it contains the expected files we
created earlier:

.. code-block:: python

    assert window.filesTable.rowCount() == 2
    assert window.filesTable.item(0, 0).text() == "video1.avi"
    assert window.filesTable.item(1, 0).text() == "video2.avi"
