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
from enum import Enum
import re

from .basic import BasicMessageValidator

RE_CHERRYPICK = re.compile(r"^\(cherry picked from commit [0-9a-fA-F]{40}\)$")
RE_GERRIT_CHANGEID = re.compile("^I[a-f0-9]{40}$")
RE_GERRIT_FOOTER = re.compile(
    r"^(?P<name>[a-z]\S+):(?P<ws>\s*)(?P<value>.*)$",
    re.IGNORECASE,
)
RE_PHABRICATOR_BUGID = re.compile("^T[0-9]+$")
RE_SUBJECT_BUG_OR_TASK = re.compile(r"^(bug|T?\d+)", re.IGNORECASE)

# Header-like lines that we are interested in validating
CORRECT_FOOTERS = [
    "Acked-by",
    "Bug",
    "Cc",
    "Change-Id",
    "Co-Authored-by",
    "Depends-On",
    "Hosts",  # Wikimedia puppet-compiler
    "Needed-By",
    "Reported-by",
    "Requested-by",
    "Reviewed-by",
    "Signed-off-by",
    "Suggested-by",
    "Tested-by",
    "Thanks",
]
FOOTERS = {footer.lower(): footer for footer in CORRECT_FOOTERS}

# A string listing all of the supported footers.
FOOTERS_STRING = ", ".join(FOOTERS.values())

BEFORE_CHANGE_ID = [
    "bug",
    "closes",
    "fixes",
    "task",
]

# Invalid footer name to expected name mapping
BAD_FOOTERS = {
    "closes": "bug",
    "fixes": "bug",
    "task": "bug",
}


def is_valid_bug_id(s):
    return RE_PHABRICATOR_BUGID.match(s)


def is_valid_change_id(s):
    """A Gerrit change id is a 40 character hex string prefixed with 'I'."""
    return RE_GERRIT_CHANGEID.match(s)


class GerritMessageValidator(BasicMessageValidator):
    """
    An iterator to validate Gerrit remote repo commit message.

    Checks:
    - First line <=80 characters or /^Revert ".*"$/
    - Second line blank
    - No line >100 characters (unless it is only a URL)
    - Footer lines ("Foo: ...") are capitalized and have a space after the ':'
    - "Bug: " is followed by one task id ("Tnnnn")
    - "Depends-On:" is followed by one change id ("I...")
    - "Needed-By:" is followed by one change id ("I...")
    - "Change-Id:" is followed one change id ("I...")
    - No "Task: ", "Fixes: ", "Closes: " lines
    """

    class MessageContext(Enum):
        HEADER = 1
        BODY = 2
        FOOTER = 3

    def __init__(self, lines):
        """
        MessageValidator for Gerrit remote origin.

        :param lines: list of lines from the commit message that will be
                      checked.
        """
        super().__init__(lines)

        self._commit_message_context = None
        self._first_changeid = False

    def check_line(self, lineno):
        yield from super().check_line(lineno)

        line_context = self.get_context(lineno)
        line = self._lines[lineno]

        if line_context is self.MessageContext.HEADER and RE_SUBJECT_BUG_OR_TASK.match(
            line,
        ):
            yield "Do not define bug in the header"

        if not line and line_context is self.MessageContext.FOOTER:
            yield "Unexpected blank line"

        gerrit_footer_match = RE_GERRIT_FOOTER.match(line)
        if gerrit_footer_match:
            name = gerrit_footer_match.group("name")
            normalized_name = name.lower()
            ws = gerrit_footer_match.group("ws")
            value = gerrit_footer_match.group("value")

            if normalized_name in BAD_FOOTERS:
                # Treat as the correct name for the rest of the rules
                normalized_name = BAD_FOOTERS[normalized_name]

            if normalized_name not in FOOTERS:
                if line_context is self.MessageContext.FOOTER:
                    yield f"Unexpected footer '{name}'.\nSupported footers: {FOOTERS_STRING}"
                else:
                    # Meh. Not a name we care about
                    return
            elif line_context is not self.MessageContext.FOOTER:
                yield f"Expected '{name}:' to be in footer"

            correct_name = FOOTERS.get(normalized_name)
            if correct_name and correct_name != name:
                yield f"Use '{correct_name}:' not '{name}:'"

            if normalized_name == "bug":
                if not is_valid_bug_id(value):
                    yield "Bug: value must be a single phabricator task ID"

            elif normalized_name == "depends-on":
                if not is_valid_change_id(value):
                    yield "Depends-On: value must be a single Gerrit change id"

            elif normalized_name == "needed-by":
                if not is_valid_change_id(value):
                    yield "Needed-By: value must be a single Gerrit change id"

            elif normalized_name == "change-id":
                if not is_valid_change_id(value):
                    yield "Change-Id: value must be a single Gerrit change id"
                if self._first_changeid is not False:
                    yield (
                        "Extra Change-Id found, first at "
                        "{}".format(self._first_changeid)
                    )
                else:
                    self._first_changeid = lineno + 1

            if (
                normalized_name in BEFORE_CHANGE_ID
                and self._first_changeid is not False
            ):
                yield ("Expected '{}:' to come before Change-Id on line " "{}").format(
                    name,
                    self._first_changeid,
                )

            if ws != " ":
                yield "Expected one space after '%s:'" % name

        elif line and line_context is self.MessageContext.FOOTER:
            # if it wasn't a footer (not a match) but it is in the footers
            cherry_pick = RE_CHERRYPICK.match(line)
            if cherry_pick:
                if lineno < len(self._lines) - 1:
                    yield "Cherry pick line is not the last line"
            else:
                yield "Expected footer line to follow format of 'Name: ...'"

    def check_global(self):
        yield from super().check_global()

        if self._first_changeid is False:
            yield "Expected Change-Id"

    def get_context(self, lineno):
        """
        Get the context of the current line.

        :param lineno: Line number that the context will be checked.
        :return:       A `MessageContext` enum.
        """
        if lineno == 0:
            # First line in the commit message is HEADER.
            self._commit_message_context = self.MessageContext.HEADER
        elif self._commit_message_context is not self.MessageContext.FOOTER:
            line = self._lines[lineno]
            footer_match = RE_GERRIT_FOOTER.match(line)
            cherrypick_match = RE_CHERRYPICK.match(line)

            if (
                (footer_match and footer_match.group("name").lower() in FOOTERS)
                or cherrypick_match
            ) and not self._lines[lineno - 1]:
                # If the current line is a footer ("Name: ..." formatted)
                # and it's indeed a footer (the "Name" listed in the FOOTERS)
                # or it's a cherry pick
                # and the previous line is a blank line.
                # Mark the current line until the end as FOOTER.
                self._commit_message_context = self.MessageContext.FOOTER
            else:
                self._commit_message_context = self.MessageContext.BODY

        return self._commit_message_context
