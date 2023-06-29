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
import dataclasses


@dataclasses.dataclass
class ValidationFailure:
    """Notice of a validation failure."""

    rule_id: str
    lineno: int
    message: str

    def __str__(self):
        return f"Line {self.lineno}: {self.message}"


class MessageValidator:
    """MessageValidator is an iterable class that will yields a tuple
    that contains line number and a string that describes the
    error.

    A class that implements this class, may implement:

    - `check_line()`, that yields the error message of the checked line.
    - `check_global()` (optional) that yields the error message of the
    checked lines, will be called after `check_line()` done the checking.

    Example usage:

    >>> lines = ['Subject', 'This should be empty', 'Body']
    >>>
    >>> class AMessageValidator(MessageValidator):
    ...     def check_line(self, lineno, line):
    ...         if lineno == 2 and line:
    ...             yield ValidationFailure(
    ...                 "L1",
    ...                 lineno,
    ...                 "Line should be empty",
    ...             )
    ...     def check_global(self, lines):
    ...         yield ValidationFailure(
    ...             "G1",
    ...             len(lines),
    ...             "Message commit is {0} lines long".format(len(lines)),
    ...         )
    ...
    >>> validator = AMessageValidator()
    >>> for err in validator.validate(lines):
    ...     print(err)
    ...
    Line 2: Line should be empty
    Line 3: Message commit is 3 lines long
    """

    def validate(self, lines):
        """Validate a commit message.

        :param lines: Commit message lines
        :return: :class:`collections.abc.Generator[ValidationFailure]`
        """
        for lineno, line in enumerate(lines):
            yield from self.check_line(lineno + 1, line)

        try:
            yield from self.check_global(lines)
        except NotImplementedError:
            pass

    def check_line(self, lineno, line):  # noqa: U100 Unused argument
        """
        A function that will be called to check the commit message.

        This function should yield class::`ValidationFailure` instances.

        :param lineno: int, line number that's being checked right now.
        :param line: line that is being checked
        :return: :class:`collections.abc.Generator[ValidationFailure]`
        """
        raise NotImplementedError(
            "`check_line()` should be implemented in {}".format(
                type(self).__name__,
            ),
        )

    def check_global(self, lines):  # noqa: U100 Unused argument
        """
        All checks that are done after the line checks.

        :param lines: Commit message lines
        :return: :class:`collections.abc.Generator[ValidationFailure]`
        """
        raise NotImplementedError(
            "`check_global()` isn't implemented in {}".format(
                type(self).__name__,
            ),
        )
