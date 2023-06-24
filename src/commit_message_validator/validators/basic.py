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
import re

from .abstract import MessageValidator

RE_URL = re.compile(r"^<?https?://\S+>?$", re.IGNORECASE)
RE_REVERT_SUBJECT = re.compile('^Revert ".*"$')


class BasicMessageValidator(MessageValidator):
    """
    An iterator to validate all remote repo commit message.

    Checks:
    - First line <=80 characters or /^Revert ".*"$/
    - Second line blank
    - No line >100 characters (unless it is only a URL)

    Global checks:
    - At least 3 lines in a commit message
    """

    def check_line(self, lineno):
        line = self._lines[lineno]

        # First line <=80
        if lineno == 0 and len(line) > 80:
            if not RE_REVERT_SUBJECT.match(line):
                yield "First line should be <=80 characters"

        # Second line blank
        elif lineno == 1 and line:
            yield "Second line should be empty"

        # No line >100 characters (unless it is only a URL)
        elif len(line) > 100 and not RE_URL.match(line):
            yield "Line should be <=100 characters"

    def check_global(self):
        # At least 3 lines in a commit message
        if len(self._lines) < 3:
            yield "Expected at least 3 lines"
