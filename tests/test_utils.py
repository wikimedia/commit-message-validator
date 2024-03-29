# Copyright (c) 2024 Wikimedia Foundation and contributors.
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
from commit_message_validator.utils import commit_message_cleanup_strip


def test_commit_message_cleanup_strip():
    lines = [
        "",
        "",
        "Commit subject",
        "",
        "Commit body message",
        "",
        "  \t",
        "",
        "Trailer: something  ",
        "",
        "# Commentary",
        "# Commentary",
        "# Commentary",
        "",
        "",
    ]
    expected_result = [
        "Commit subject",
        "",
        "Commit body message",
        "",
        "Trailer: something",
    ]
    result = commit_message_cleanup_strip(lines)
    print(result)
    assert result == expected_result
