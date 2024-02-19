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
from .rules import BodyMaxLength
from .rules import ChangeIdExpected
from .rules import ChangeIdRequired
from .rules import CherryPickLast
from .rules import CommitMinLines
from .rules import CommitSecondLineEmpty
from .rules import ExpectedTrailers
from .rules import PhabricatorTaskIdExpected
from .rules import RulesMessageValidator
from .rules import SubjectMaxLength
from .rules import SubjectNoBugOrTask
from .rules import TrailerInBody
from .rules import TrailerNoBlankLines
from .rules import UnexpectedTrailerLine

# Header-like lines that we are interested in validating
EXPECTED_TRAILERS = [
    "Acked-by",
    "Bug",
    "Cc",
    "Change-Id",
    "Co-Authored-by",
    "Depends-On",
    "Hosts",  # Wikimedia puppet-compiler
    "Change-Private",  # Wikimedia puppet-compiler
    "Needed-By",
    "Reported-by",
    "Requested-by",
    "Reviewed-by",
    "Signed-off-by",
    "Suggested-by",
    "Tested-by",
    "Thanks",
]
NORMALIZED_EXPECTED_TRAILERS = [name.lower() for name in EXPECTED_TRAILERS]

BEFORE_CHANGE_ID = [
    "bug",
    "closes",
    "fixes",
    "task",
]

# Invalid trailer name to expected name mapping
BAD_TRAILERS = {
    "closes": "bug",
    "fixes": "bug",
    "task": "bug",
}


class GerritMessageValidator(RulesMessageValidator):
    """Validate a Gerrit remote repo commit message."""

    def __init__(self):
        super().__init__(
            line_rules=[
                SubjectMaxLength(),
                SubjectNoBugOrTask(),
                BodyMaxLength(),
                TrailerInBody(
                    expected=NORMALIZED_EXPECTED_TRAILERS + list(BAD_TRAILERS.keys()),
                ),
                TrailerNoBlankLines(),
                ExpectedTrailers(EXPECTED_TRAILERS, fixup=BAD_TRAILERS),
                PhabricatorTaskIdExpected(["bug"], fixup=BAD_TRAILERS),
                ChangeIdExpected(["depends-on", "needed-by", "change-id"]),
                UnexpectedTrailerLine(),
            ],
            commit_rules=[
                CommitMinLines(),
                CommitSecondLineEmpty(),
                CherryPickLast(),
                ChangeIdRequired(before=BEFORE_CHANGE_ID),
            ],
            expected_trailers=NORMALIZED_EXPECTED_TRAILERS,
        )


class GitLabMessageValidator(RulesMessageValidator):
    """Validate a GitLab remote repo commit message."""

    def __init__(self):
        super().__init__(
            line_rules=[
                SubjectMaxLength(),
                SubjectNoBugOrTask(),
                BodyMaxLength(),
                TrailerInBody(
                    expected=NORMALIZED_EXPECTED_TRAILERS + list(BAD_TRAILERS.keys()),
                ),
                TrailerNoBlankLines(),
                ExpectedTrailers(EXPECTED_TRAILERS, fixup=BAD_TRAILERS),
                PhabricatorTaskIdExpected(["bug"], fixup=BAD_TRAILERS),
                UnexpectedTrailerLine(),
            ],
            commit_rules=[
                CommitSecondLineEmpty(),
                CherryPickLast(),
            ],
            expected_trailers=NORMALIZED_EXPECTED_TRAILERS,
        )
