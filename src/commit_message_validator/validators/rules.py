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
from enum import Enum
import re
import typing

from .core import MessageValidator
from .core import ValidationFailure

RE_CHERRYPICK = re.compile(r"^\(cherry picked from commit [0-9a-fA-F]{40}\)$")
RE_TRAILER = re.compile(
    r"^(?P<name>[a-z]\S+):(?P<ws>\s*)(?P<value>.*)$",
    re.IGNORECASE,
)


class MessageContext(Enum):
    SUBJECT = 1
    BODY = 2
    TRAILER = 3


@dataclasses.dataclass
class Rule:
    """A validation rule for a commit message."""

    id: typing.ClassVar[str]
    name: typing.ClassVar[str]


@dataclasses.dataclass
class LineRule(Rule):
    """A validation rule for a single line of a commit message."""

    def validate(self, lineno, line, context):  # noqa: U100 Unused argument
        """Validate a line from a commit message."""
        raise NotImplementedError(
            "`validate()` should be implemented in {}".format(
                type(self).__name__,
            ),
        )


class LineLengthRule(LineRule):
    """Ensure that a line does not exceed max_len characters."""

    max_len: typing.ClassVar[int]
    msg = "Line exceeds max length ({0}>{1})"
    ctx: typing.Optional[MessageContext] = None

    def validate(self, lineno, line, context):
        if self.ctx and context != self.ctx:
            return
        line_len = len(line)
        if line_len > self.max_len:
            yield ValidationFailure(
                self.id,
                lineno,
                self.msg.format(line_len, self.max_len),
            )


@dataclasses.dataclass
class LineRegexNoMatchRule(LineRule):
    """Ensure that no line matches a given regex."""

    regex: typing.ClassVar[typing.re.Pattern[str]]
    msg: typing.ClassVar[str]
    ctx: typing.ClassVar[MessageContext]

    def validate(self, lineno, line, context):
        if self.ctx and context != self.ctx:
            return
        if self.regex.search(line):
            yield ValidationFailure(self.id, lineno, self.msg)


class SubjectMaxLength(LineLengthRule):
    """First line <=80 characters or /^Revert ".*"$/"""

    id = "S1"
    name = "subject-max-length"
    ctx = MessageContext.SUBJECT
    msg = "Subject must be <=80 characters"
    max_len = 80

    RE_REVERT = re.compile(r'^Revert ".*"$')

    def validate(self, lineno, line, context):
        if context != self.ctx:
            return
        if not self.RE_REVERT.match(line):
            yield from super().validate(lineno, line, context)


class SubjectNoBugOrTask(LineRegexNoMatchRule):
    """Do not allow 'bug' or a Phabricator task ID in subject."""

    id = "S2"
    name = "subject-no-bug-or-task"
    ctx = MessageContext.SUBJECT
    regex = re.compile(r"^(bug|T?\d+)", re.IGNORECASE)
    msg = "Do not define bug in the subject"


class BodyMaxLength(LineLengthRule):
    """No line >100 characters (unless it is only a URL)"""

    id = "B1"
    name = "body-max-length"
    ctx = MessageContext.BODY
    max_len = 100

    RE_URL = re.compile(r"^<?https?://\S+>?$", re.IGNORECASE)

    def validate(self, lineno, line, context):
        if context != self.ctx:
            return
        if not self.RE_URL.match(line):
            yield from super().validate(lineno, line, context)


class TrailerNoBlankLines(LineRule):
    """No blank lines allowed between trailer lines."""

    id = "F1"
    name = "trailer-no-blanks"
    ctx = MessageContext.TRAILER

    def validate(self, lineno, line, context):
        if context != self.ctx:
            return
        if not line:
            yield ValidationFailure(self.id, lineno, "Unexpected blank line")


@dataclasses.dataclass
class TrailerInBody(LineRule):
    """No '^Name: value$' lines allowed in body."""

    id = "F2"
    name = "trailer-in-body"
    ctx = MessageContext.BODY
    expected: typing.Optional[typing.Sequence[str]] = None

    def validate(self, lineno, line, context):
        if context != self.ctx:
            return
        m = RE_TRAILER.match(line)
        if m:
            name = m.group("name")
            normalized = name.lower()
            if self.expected and normalized not in self.expected:
                return
            yield ValidationFailure(
                self.id,
                lineno,
                f"Expected '{name}:' to be in trailer",
            )


class TrailerLineRule(LineRule):
    """A validation rule for a commit message trailer line."""

    def validate(self, lineno, line, context):
        m = RE_TRAILER.match(line)
        if not m:
            return
        name = m.group("name")
        normalized_name = name.lower()
        ws = m.group("ws")
        value = m.group("value")
        yield from self.validate_trailer(
            lineno,
            name,
            normalized_name,
            ws,
            value,
            context,
        )


@dataclasses.dataclass
class ExpectedTrailers(TrailerLineRule):
    """Ensure that trailers have expected names and formatting."""

    id = "F3"
    name = "expected-trailer-format"
    expected: typing.Sequence[str]
    fixup: typing.Optional[typing.Dict[str, str]] = None

    def validate_trailer(
        self,
        lineno,
        name,
        normalized_name,
        ws,
        value,  # noqa: U100 Unused argument
        context,
    ):
        trailers = {trailer.lower(): trailer for trailer in self.expected}
        if self.fixup and normalized_name in self.fixup:
            # Treat as the correct name for the rest of the checks
            normalized_name = self.fixup[normalized_name]

        if normalized_name not in trailers.keys():
            if context is MessageContext.TRAILER:
                supported = ", ".join(trailers.values())
                yield ValidationFailure(
                    self.id,
                    lineno,
                    f"Unexpected trailer '{name}'. Supported trailers: {supported}",
                )
            else:
                # Not a expected trailer, so skip additional checks
                return

        correct_name = trailers.get(normalized_name)
        if correct_name and correct_name != name:
            yield ValidationFailure(
                "F4",
                lineno,
                f"Use '{correct_name}:' not '{name}:'",
            )

        if ws != " ":
            yield ValidationFailure(
                "F5",
                lineno,
                f"Expected one space after '{name}:'",
            )


@dataclasses.dataclass
class PhabricatorTaskIdExpected(TrailerLineRule):
    """Trailer value must be a Phabricator task ID"""

    id = "F6"
    name = "phabricator-task-id-expected"
    names: typing.Sequence[str]
    fixup: typing.Optional[typing.Dict[str, str]] = None

    RE_BUGID = re.compile("^T[0-9]+$")

    def validate_trailer(
        self,
        lineno,
        name,  # noqa: U100 Unused argument
        normalized_name,
        ws,  # noqa: U100 Unused argument
        value,
        context,  # noqa: U100 Unused argument
    ):
        if self.fixup and normalized_name in self.fixup:
            # Treat as the correct name for the rest of the checks
            normalized_name = self.fixup[normalized_name]
        if normalized_name == "bug" and not self.RE_BUGID.match(value):
            yield ValidationFailure(
                self.id,
                lineno,
                "Bug: value must be a single phabricator task ID",
            )


@dataclasses.dataclass
class ChangeIdExpected(TrailerLineRule):
    """Trailer value must be a Gerrit change id."""

    id = "F7"
    name = "change-id-value-expected"
    names: typing.Sequence[str]
    fixup: typing.Optional[typing.Dict[str, str]] = None

    RE_CHANGEID = re.compile("^I[a-f0-9]{40}$")

    def validate_trailer(
        self,
        lineno,
        name,
        normalized_name,
        ws,  # noqa: U100 Unused argument
        value,
        context,  # noqa: U100 Unused argument
    ):
        if self.fixup and normalized_name in self.fixup:
            # Treat as the correct name for the rest of the checks
            normalized_name = self.fixup[normalized_name]
        if normalized_name in self.names and not self.RE_CHANGEID.match(value):
            yield ValidationFailure(
                self.id,
                lineno,
                f"{name}: value must be a single Gerrit change id",
            )


class UnexpectedTrailerLine(LineRule):
    """Ensure that all trailer lines are either 'name: value' or
    a cherry-pick indicator."""

    id = "F8"
    name = "unexpected-trailer-line"

    def validate(self, lineno, line, context):
        if context is not MessageContext.TRAILER:
            return
        if not line:
            return
        if not RE_TRAILER.match(line) and not RE_CHERRYPICK.match(line):
            yield ValidationFailure(
                self.id,
                lineno,
                "Expected trailer line to follow format of 'Name: ...'",
            )


@dataclasses.dataclass
class CommitRule(Rule):
    """A validation rule for an entire commit message."""

    msg: typing.ClassVar[str]

    def validate(self, lines):  # noqa: U100 Unused argument
        """Validate a commit message."""
        raise NotImplementedError(
            "`validate()` should be implemented in {}".format(
                type(self).__name__,
            ),
        )


class CommitSecondLineEmpty(CommitRule):
    """Second line of commit message must be blank."""

    id = "C1"
    name = "commit-second-line-empty"

    def validate(self, lines):
        if len(lines) > 1 and lines[1]:
            yield ValidationFailure(self.id, 2, "Second line should be empty")


class CommitMinLines(CommitRule):
    """Commit message must have at least 3 lines."""

    id = "C2"
    name = "commit-min-lines"

    def validate(self, lines):
        if len(lines) < 3:
            yield ValidationFailure(self.id, len(lines), "Expected at least 3 lines")


class CherryPickLast(CommitRule):
    """A cherry-pick description should be the last line if present."""

    id = "C3"
    name = "cherry-pick-last-line"

    def validate(self, lines):
        last_line = len(lines) - 1
        for lineno, line in enumerate(lines):
            if RE_CHERRYPICK.match(line) and lineno != last_line:
                yield ValidationFailure(
                    self.id,
                    lineno + 1,
                    "Cherry pick line is not the last line",
                )


@dataclasses.dataclass
class ChangeIdRequired(CommitRule):
    """One and only one Change-Id line must be present."""

    id = "C4"
    name = "change-id-required"
    before: typing.Optional[typing.Sequence[str]] = None

    def validate(self, lines):
        changeid = False
        for lineno, line in enumerate(lines):
            m = RE_TRAILER.match(line)
            if m:
                normalized = m.group("name").lower()
                if normalized == "change-id":
                    if not changeid:
                        changeid = lineno + 1
                    else:
                        yield ValidationFailure(
                            self.id,
                            lineno + 1,
                            f"Extra Change-Id found, first at {changeid}",
                        )
                elif self.before and normalized in self.before and changeid:
                    name = m.group("name")
                    yield ValidationFailure(
                        "C5",
                        lineno + 1,
                        f"Expected '{name}:' to come before Change-Id on line "
                        f"{changeid}",
                    )

        if not changeid:
            yield ValidationFailure("C6", len(lines), "Expected Change-Id")


class RulesMessageValidator(MessageValidator):
    """Validate commit messages based on configured rules."""

    def __init__(
        self,
        line_rules=None,
        commit_rules=None,
        expected_trailers=None,
    ):
        """
        :param line_rules: Collection of :class:`LineRule` objects
        :param commit_rules: Collection of :class:`CommitRule` objects
        :param expected_trailers: Collection of normalized trailer names
        """
        self._line_rules = line_rules or []
        self._commit_rules = commit_rules or []
        self._expected_trailers = expected_trailers or []
        self._message_context = None
        super().__init__()

    def validate(self, lines):
        self._lines = lines
        yield from super().validate(lines)

    def check_line(self, lineno, line):
        context = self.get_context(lineno - 1, self._lines)
        for rule in self._line_rules:
            yield from rule.validate(lineno, line, context)

    def check_global(self, lines):
        for rule in self._commit_rules:
            yield from rule.validate(lines)

    def get_context(self, lineno, lines):
        """Get the context of the current line.

        :param lineno: 0-indexed line number to compute context for.
        :param lines: commit message lines
        :return: :class:`MessageContext`
        """
        if lineno == 0:
            # First line in the commit message is subject.
            self._message_context = MessageContext.SUBJECT

        elif not self._expected_trailers:
            self._message_context = MessageContext.BODY

        elif self._message_context is not MessageContext.TRAILER:
            line = lines[lineno]
            trailer_match = RE_TRAILER.match(line)
            cherrypick_match = RE_CHERRYPICK.match(line)

            if (
                (
                    trailer_match
                    and trailer_match.group("name").lower() in self._expected_trailers
                )
                or cherrypick_match
            ) and not lines[lineno - 1]:
                # If the current line is a trailer ("Name: ..." formatted)
                # or it's a cherry pick
                # and the previous line is a blank line.
                # Mark the current line until the end as TRAILER.
                self._message_context = MessageContext.TRAILER
            else:
                self._message_context = MessageContext.BODY

        return self._message_context
