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

from .rules import BodyMaxLength
from .rules import CommitSecondLineEmpty
from .rules import LineRegexNoMatchRule
from .rules import MessageContext
from .rules import RulesMessageValidator
from .rules import SubjectMaxLength


class GitHubSubjectNoBugNumber(LineRegexNoMatchRule):
    id = "GH1"
    name = "github-subject-no-bug-number"
    ctx = MessageContext.SUBJECT
    regex = re.compile(r"#\d+")
    msg = "Do not define bug in the subject"


class GitHubNoForeignClose(LineRegexNoMatchRule):
    id = "GH2"
    name = "github-no-foreign-close"
    ctx = MessageContext.BODY
    regex = re.compile(
        r"^(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+\S+/\S+#\d+",
        re.IGNORECASE,
    )
    msg = (
        'Do not write "closing issue keywords" for closing an issue '
        "that is in another repository"
    )


class GitHubMessageValidator(RulesMessageValidator):
    """Validate a GitHub remote repo commit message."""

    def __init__(self):
        super().__init__(
            line_rules=[
                SubjectMaxLength(),
                BodyMaxLength(),
                GitHubSubjectNoBugNumber(),
                GitHubNoForeignClose(),
            ],
            commit_rules=[
                CommitSecondLineEmpty(),
            ],
        )
