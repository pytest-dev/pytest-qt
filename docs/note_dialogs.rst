A note about Modal Dialogs
==========================

Simple Dialogs
--------------

For QMessageBox.question one approach is to mock the function using the `monkeypatch <https://docs.pytest.org/en/latest/monkeypatch.html>`_ fixture:

.. code-block:: python

    def test_Qt(qtbot, monkeypatch):
        simple = Simple()
        qtbot.addWidget(simple)

        monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)
        simple.query()
        assert simple.answer

Custom Dialogs
--------------

Suppose you have a custom dialog that asks the user for their name and age, and a form
that uses it. One approach is to add a convenience function that also has the nice
benefit of making testing easier, like this:

.. code-block:: python

   class AskNameAndAgeDialog(QDialog):
       @classmethod
       def ask(cls, text, parent):
           dialog = cls(parent)
           dialog.text.setText(text)
           if dialog.exec_() == QDialog.Accepted:
               return dialog.getName(), dialog.getAge()
           else:
               return None, None

This allows clients of the dialog to use it this way:

.. code-block:: python

   name, age = AskNameAndAgeDialog.ask("Enter name and age because of bananas:", parent)
   if name is not None:
       # use name and age for bananas
       ...

And now it is also easy to mock ``AskNameAndAgeDialog.ask`` when testing the form:

.. code-block:: python

    def test_form_registration(qtbot, monkeypatch):
        form = RegistrationForm()

        monkeypatch.setattr(
            AskNameAndAgeDialog, "ask", classmethod(lambda *args: ("Jonh", 30))
        )
        qtbot.click(form.enter_info())
        # calls AskNameAndAgeDialog.ask
        # test that the rest of the form correctly behaves as if
        # user entered "Jonh" and 30 as name and age
