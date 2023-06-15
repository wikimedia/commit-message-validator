#!/usr/bin/env python

"""
Runs through the provided git repo and samples the commit
messages to see whether they would pass the commit message
validator.
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
