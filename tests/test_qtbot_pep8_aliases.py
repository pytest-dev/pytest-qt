import inspect
from unittest.mock import MagicMock

import pytest

from pytestqt.qtbot import QtBot


def _format_pep_8(camel_case_name: str) -> str:
    """
    Helper that creates a pep8_compliant_method_name
    from a given camelCaseMethodName.
    """
    return camel_case_name[0].lower() + "".join(
        f"_{letter.lower()}" if letter.isupper() else letter.lower()
        for letter in camel_case_name[1:]
    )


@pytest.mark.parametrize(
    "expected, camel_case_input",
    [
        ("add_widget", "addWidget"),
        ("wait_active", "waitActive"),
        ("wait_exposed", "waitExposed"),
        ("wait_for_window_shown", "waitForWindowShown"),
        ("wait_signal", "waitSignal"),
        ("wait_signals", "waitSignals"),
        ("assert_not_emitted", "assertNotEmitted"),
        ("wait_until", "waitUntil"),
        ("wait_callback", "waitCallback"),
    ],
)
def test_format_pep8(expected: str, camel_case_input: str):
    assert _format_pep_8(camel_case_input) == expected


def test_pep8_aliases(qtbot):
    """
    Test that defined PEP8 aliases actually refer to the correct implementation.
    Only check methods that have such an alias defined.
    """
    for name, func in inspect.getmembers(qtbot, inspect.ismethod):
        if name != name.lower():
            pep8_name = _format_pep_8(name)
            if hasattr(qtbot, pep8_name):
                # Found a PEP8 alias.
                assert (
                    getattr(qtbot, name).__func__ is getattr(qtbot, pep8_name).__func__
                )


def generate_test_cases_for_test_subclass_of_qtbot_has_overwritten_pep8_aliases():
    """
    For each PEP8 alias found in QtBot, yields a test case consisting of
    a QtBot subclass that has the alias pair’s camelCase implementation
    overwritten with a MagicMock.

    Yields tuples (subclass, camelCaseMethodName, pep8_method_name_alias)
    """
    for name, func in inspect.getmembers(QtBot, inspect.isfunction):
        if name != name.lower():
            subclass_logic_mock = MagicMock()
            pep8_name = _format_pep_8(name)
            if hasattr(QtBot, pep8_name):
                # Found a PEP8 alias.
                methods = QtBot.__dict__.copy()
                # Only overwrite the camelCase method
                methods[name] = subclass_logic_mock
                sub_class = type("QtBotSubclass", (QtBot,), methods)
                yield sub_class, name, pep8_name


@pytest.mark.parametrize(
    "qtbot_subclass, method_name, pep8_name",
    generate_test_cases_for_test_subclass_of_qtbot_has_overwritten_pep8_aliases(),
)
def test_subclass_of_qtbot_has_overwritten_pep8_aliases(
    qtbot_subclass, method_name: str, pep8_name: str
):
    """
    Test that subclassing QtBot does not create surprises,
    by checking that the PEP8 aliases follow overwritten
    camelCase methods.
    """
    instance: QtBot = qtbot_subclass(MagicMock())
    assert isinstance(getattr(instance, method_name), MagicMock)
    assert isinstance(getattr(instance, pep8_name), MagicMock)
    # Now call the pep8_name_method and check that the subclass’s
    # camelCaseMethod implementation was actually called.
    getattr(instance, pep8_name)()
    getattr(instance, method_name).assert_called()
