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
from commit_message_validator.validators import RulesMessageValidator
from commit_message_validator.validators.rules import MessageContext


def test_get_context():
    lines = [
        "Commit subject",
        "",
        "Commit body message",
        "",
        "Change-Id: I00d0f7c3b294c3ddc656f9a5447df89c63142203",
    ]

    validator = RulesMessageValidator(expected_footers=["change-id"])

    expected_result = [
        MessageContext.SUBJECT,
        MessageContext.BODY,
        MessageContext.BODY,
        MessageContext.BODY,
        MessageContext.FOOTER,
    ]

    result = [validator.get_context(lineno, lines) for lineno in range(len(lines))]
    assert result == expected_result
