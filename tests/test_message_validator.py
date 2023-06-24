# Copyright (c) 2023 Wikimedia Foundation and contributors.
# All Rights Reserved.
#
# This file is part of Commit Message Validator.
#
# Commit Message Validator is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Commit Message Validator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Commit Message Validator.  If not, see <http://www.gnu.org/licenses/>.
import pytest

from commit_message_validator.validators import MessageValidator


class NoCheckLineMessageValidator(MessageValidator):
    """
    A MessageValidator that doesn't implement `check_line()` and
    `check_global()`.
    """


class JustTestMessageValidator(MessageValidator):
    def check_line(self, lineno):
        if lineno == 1:
            yield "Error on line 2"
        elif lineno == 3:
            yield "Error on line 4"

    def check_global(self):
        yield "From global check"


class NoCheckGlobalMessageValidator(MessageValidator):
    def check_line(self, lineno):
        if lineno == 1:
            yield "Error on line 2"
        elif lineno == 3:
            yield "Error on line 4"


class TestMessageValidator:
    def test_check_line_not_implemented(self):
        # If 'check_line()` is not implemented, the method should raise
        # NotImplementedError.
        lines = ["This is a line"]
        no_check_line_mv = NoCheckLineMessageValidator(lines)
        with pytest.raises(NotImplementedError) as e:
            no_check_line_mv.check_line(0)
        assert (
            str(e.value)
            == "`check_line()` should be implemented in NoCheckLineMessageValidator"
        )

    def test_check_global_not_implemented_but_called(self):
        # If 'check_global()` is not implemented, but called,
        # the method should raise NotImplementedError.
        lines = ["This is a line"]
        no_check_line_mv = NoCheckLineMessageValidator(lines)

        with pytest.raises(NotImplementedError) as e:
            no_check_line_mv.check_global()
        assert (
            str(e.value)
            == "`check_global()` isn't implemented in NoCheckLineMessageValidator"
        )

    def test_iterate_iterable_message_validator(self):
        lines = ["This is a line", "2nd line", "3rd line", "4th line", "5th"]

        expected_result = [
            (lineno, msg) for lineno, msg in JustTestMessageValidator(lines)
        ]
        assert expected_result == [
            (2, "Error on line 2"),
            (4, "Error on line 4"),
            (5, "From global check"),
        ]

    def test_iterate_iterable_message_validator_no_check_global(self):
        lines = ["This is a line", "2nd line", "3rd line", "4th line", "5th"]

        expected_result = [
            (lineno, msg) for lineno, msg in NoCheckGlobalMessageValidator(lines)
        ]
        assert expected_result == [
            (2, "Error on line 2"),
            (4, "Error on line 4"),
        ]

    def test_iterate_with_next_method(self):
        lines = ["This is a line", "2nd line", "3rd line", "4th line", "5th"]

        just_test_mv = JustTestMessageValidator(lines)
        assert (2, "Error on line 2") == just_test_mv.next()
