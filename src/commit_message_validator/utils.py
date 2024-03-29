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
import subprocess
import sys


def check_output(*args):
    """Wrapper around subprocess to handle Python 3"""
    return subprocess.check_output(args).decode("utf8")


def ansi_codes():
    """Get ANSI escape sequences for coloring error output.

    Can be configured using .gitconfig settings to disable or change color
    from the default red text.

    Disable color output:
        git config color.commit_message_validator false

    Force color output:
        git config color.commit_message_validator true

    Change color:
        git config color.commit_message_validator.error yellow
    """
    stdout_is_tty = "true" if sys.stdout.isatty() else "false"
    try:
        # Ask git if colors should be used
        # Raises CalledProcessError if disabled
        check_output(
            "git",
            "config",
            "--get-colorbool",
            "color.commit_message_validator",
            stdout_is_tty,
        )
        # Get configured color code (default to red text)
        return (
            check_output(
                "git",
                "config",
                "--get-color",
                "color.commit_message_validator.error",
                "red",
            ),
            "\x1b[0m",
        )
    except subprocess.CalledProcessError:  # pragma: no cover
        return "", ""


def commit_message_cleanup_strip(lines):
    """Cleanup input in the style of `git commit --cleanup=strip`.

    - Strip leading and trailing empty lines
    - Strip commentary
    - Strip trailing whitespace
    - Collapse consecutive empty lines
    """

    def pop_matching(predicate, idx=-1):
        while predicate(lines[idx]):
            lines.pop(idx)

    pop_matching(lambda x: x == "", idx=0)  # Discard empty leading lines
    pop_matching(lambda x: x == "")  # Discard empty trailing lines
    pop_matching(lambda x: x.startswith("#"))  # Discard commentary
    pop_matching(lambda x: x == "")  # Discard empty trailing lines

    # Strip trailing whitespace and consolidate consecutive empty lines
    prior_line = None
    cleaned = []
    for line in lines:
        line = line.rstrip()
        if line != prior_line or prior_line != "":
            cleaned.append(line)
        prior_line = line
    return cleaned
