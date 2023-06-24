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


class MessageValidator:
    """
    MessageValidator is an iterable class that will yields a tuple
    that contains line number and a string that describes the
    error.

    A class that implements this class, may implement:

    - `check_line()`, that yields the error message of the checked line.
    - `check_global()` (optional) that yields the error message of the
    checked lines, will be called after `check_line()` done the checking.

    See `GerritMessageValidator` for an implementation of
    `check_line()`, and `check_global()` methods.

    Example usage:

    >>> lines = ['Title', 'This should be empty', 'Body']
    >>>
    >>> class AMessageValidator(MessageValidator):
    ...     def check_line(self, lineno):
    ...         line = self._lines[lineno]
    ...         if lineno == 1 and line:
    ...             yield 'Line should be empty'
    ...     def check_global(self):
    ...         yield 'Message commit is {0} lines long'.format(
    ...             len(self._lines))
    ...
    >>> for lineno, msg in AMessageValidator(lines):
    ...     print('{0} {1}'.format(lineno, msg))
    ...
    2 Line should be empty
    3 Message commit is 3 lines long

    """

    def __init__(self, lines):
        """
        Constructor for MessageValidator.

        :param lines: list of lines from a commit message that will be checked.
        """
        self._lines = lines
        self._generator = self._check_generator()

    def check_line(self, lineno):  # noqa: U100 Unused argument 'lineno'
        """
        A function that will be called to check the commit message.

        This function should yields a string that contain description
        of what error that occured on `lineno`.

        :param lineno:       int, line number that's being checked right now.
        """
        raise NotImplementedError(
            "`check_line()` should be implemented in {}".format(
                type(self).__name__,
            ),
        )

    def check_global(self):
        """
        All checks that are done after the line checks.

        This function should yields a string that contain description
        of what error that is occured.
        """
        raise NotImplementedError(
            "`check_global()` isn't implemented in {}".format(
                type(self).__name__,
            ),
        )

    def _check_generator(self):
        """
        A generator returning each error and line number.
        """
        for lineno in range(len(self._lines)):
            for e in self.check_line(lineno):
                yield lineno + 1, e

        try:
            for e in self.check_global():
                yield len(self._lines), e
        except NotImplementedError:
            pass

    def __iter__(self):
        return self

    def __next__(self):
        """
        Return the next error of the generator.
        """
        return next(self._generator)

    def next(self):
        # For Python 2 support
        return self.__next__()
