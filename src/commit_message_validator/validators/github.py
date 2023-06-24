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

from .basic import BasicMessageValidator

RE_GITHUB_ISSUE_NUMBER = re.compile(r"#\d+")
RE_GITHUB_CLOSE_ISSUE_IN_DIFFERENT_REPO = re.compile(
    r"^(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+\S+/\S+#\d+",
    re.IGNORECASE,
)


class GitHubMessageValidator(BasicMessageValidator):
    """
    An iterator to validate GitHub remote repo commit message.

    Checks:
    - First line <=80 characters or /^Revert ".*"$/
    - Second line blank
    - No line >100 characters (unless it is only a URL)
    - Issue should not be defined in the header
    - "Closing issue keywords" for closing an issue that is in another
    repository shouldn't be exist.
    """

    def check_line(self, lineno):
        yield from super().check_line(lineno)

        line = self._lines[lineno]

        if lineno == 0 and RE_GITHUB_ISSUE_NUMBER.findall(line):
            yield "Do not define bug in the header"

        if RE_GITHUB_CLOSE_ISSUE_IN_DIFFERENT_REPO.match(line):
            yield (
                'Do not write "closing issue keywords" for closing an issue '
                "that is in another repository"
            )
