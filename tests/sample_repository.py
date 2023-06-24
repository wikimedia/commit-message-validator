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
"""
Runs through the provided git repo and samples the commit messages to see
whether they would pass the commit message validator.
"""

import os
import sys

import commit_message_validator as cmv

if sys.version_info[0] > 2:
    from io import StringIO
else:
    from StringIO import StringIO


def main():
    if len(sys.argv) < 2:
        print("Usage: tox -e sample /path/to/git/repo [count]")
        sys.exit(1)
    repo = sys.argv[1]
    if len(sys.argv) == 3:
        num = sys.argv[2]
    else:
        num = "10"
    os.chdir(repo)
    sha1s = cmv.check_output(
        ["git", "log", "--format=%H", "--no-merges", "-n" + num],
    ).splitlines()
    good = 0
    bad = 0
    for sha1 in sha1s:
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            exit_code = cmv.validate(sha1)
            if exit_code != 0:
                saved_stdout.write("Fail: " + sha1 + "\n")
                saved_stdout.write(out.getvalue() + "\n")
                bad += 1
            else:
                saved_stdout.write("Pass: " + sha1 + "\n")
                good += 1
        finally:
            sys.stdout = saved_stdout
    bad_percent = f"{bad/(bad+good):.2%}"
    print(
        "commit-message-validator identified that %s commits failed validation."
        % bad_percent,
    )


if __name__ == "__main__":
    main()
