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
import argparse
import io
import os
import sys

from .lint import validate
from .utils import check_output


def main():
    parser = argparse.ArgumentParser(
        prog="sample-repository",
        description="Sample commits in a repo to see if they pass validation",
    )
    parser.add_argument(
        "repo",
        help="Path to git repo to check",
        metavar="/path/to/git/repo",
    )
    parser.add_argument(
        "count",
        help="Number of commits to sample",
        default=10,
        type=int,
        nargs="?",
    )
    args = parser.parse_args()

    os.chdir(args.repo)
    sha1s = check_output(
        "git",
        "log",
        "--format=%H",
        "--no-merges",
        f"-n{args.count}",
    ).splitlines()

    good = 0
    bad = 0
    for sha1 in sha1s:
        saved_stdout = sys.stdout
        try:
            out = io.StringIO()
            sys.stdout = out
            exit_code = validate(sha1)
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
