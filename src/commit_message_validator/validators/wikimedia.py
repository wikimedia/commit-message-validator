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
from .rules import ExpectedFooters
from .rules import FooterInBody
from .rules import FooterNoBlankLines
from .rules import PhabricatorTaskIdExpected
from .rules import RulesMessageValidator
from .rules import SubjectMaxLength
from .rules import SubjectNoBugOrTask
from .rules import UnexpectedFooterLine

# Header-like lines that we are interested in validating
EXPECTED_FOOTERS = [
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
NORMALIZED_EXPECTED_FOOTERS = [name.lower() for name in EXPECTED_FOOTERS]

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


class GerritMessageValidator(RulesMessageValidator):
    """Validate a Gerrit remote repo commit message."""

    def __init__(self):
        super().__init__(
            line_rules=[
                SubjectMaxLength(),
                SubjectNoBugOrTask(),
                BodyMaxLength(),
                FooterInBody(
                    expected=NORMALIZED_EXPECTED_FOOTERS + list(BAD_FOOTERS.keys()),
                ),
                FooterNoBlankLines(),
                ExpectedFooters(EXPECTED_FOOTERS, fixup=BAD_FOOTERS),
                PhabricatorTaskIdExpected(["bug"], fixup=BAD_FOOTERS),
                ChangeIdExpected(["depends-on", "needed-by", "change-id"]),
                UnexpectedFooterLine(),
            ],
            commit_rules=[
                CommitMinLines(),
                CommitSecondLineEmpty(),
                CherryPickLast(),
                ChangeIdRequired(before=BEFORE_CHANGE_ID),
            ],
            expected_footers=NORMALIZED_EXPECTED_FOOTERS,
        )


class GitLabMessageValidator(RulesMessageValidator):
    """Validate a GitLab remote repo commit message."""

    def __init__(self):
        super().__init__(
            line_rules=[
                SubjectMaxLength(),
                SubjectNoBugOrTask(),
                BodyMaxLength(),
                FooterInBody(
                    expected=NORMALIZED_EXPECTED_FOOTERS + list(BAD_FOOTERS.keys()),
                ),
                FooterNoBlankLines(),
                ExpectedFooters(EXPECTED_FOOTERS, fixup=BAD_FOOTERS),
                PhabricatorTaskIdExpected(["bug"], fixup=BAD_FOOTERS),
                UnexpectedFooterLine(),
            ],
            commit_rules=[
                CommitSecondLineEmpty(),
                CherryPickLast(),
            ],
            expected_footers=NORMALIZED_EXPECTED_FOOTERS,
        )
