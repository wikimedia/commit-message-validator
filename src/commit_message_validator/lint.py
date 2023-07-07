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
import io
import operator
import os
import sys

from .utils import ansi_codes
from .utils import check_output
from .validators import GerritMessageValidator
from .validators import GitHubMessageValidator
from .validators import GitLabMessageValidator

WIKIMEDIA_GERRIT_HOST = "gerrit.wikimedia.org"
WIKIMEDIA_GITLAB_HOST = "gitlab.wikimedia.org"
GERRIT_CHECK_FAIL_MESSAGE_SUGGESTION = (
    "Please review "
    "<https://www.mediawiki.org/wiki/Gerrit/Commit_message_guidelines>"
    "\nand update your commit message accordingly"
)


def guess_message_validator_class():
    """
    Get appropriate MessageValidator class to check the commit message
    in the repo.

    This method will check whether the remote repo is a Gerrit or GitHub, and
    return the appropriate MessageValidator class to check the commit message.

    :return: A class that implements `MessageValidator` class.
    """
    result = None
    if os.path.exists(".gitreview") and os.path.isfile(".gitreview"):
        result = check_output(
            "git",
            "config",
            "-f",
            ".gitreview",
            "--get",
            "gerrit.host",
        )

    if result and WIKIMEDIA_GERRIT_HOST in result:
        return GerritMessageValidator

    if result and WIKIMEDIA_GITLAB_HOST in result:
        return GitLabMessageValidator

    result = check_output(
        "git",
        "config",
        "--get-regex",
        "^remote.*.url$",
    )

    remotes = {
        label.split(".", maxsplit=2)[1]: url
        for label, url in (line.split(" ", maxsplit=1) for line in result.splitlines())
    }

    if WIKIMEDIA_GERRIT_HOST in {
        remotes.get("wikimedia"),
        remotes.get("gerrit"),
        remotes.get("origin"),
    }:
        return GerritMessageValidator
    elif WIKIMEDIA_GITLAB_HOST in remotes.get("origin"):
        return GitLabMessageValidator
    elif "github.com" in remotes.get("origin"):
        return GitHubMessageValidator
    else:
        # If there's nothing match just use GerritMessageValidator
        return GerritMessageValidator


def lint_message(lines, cls):
    """Lint a commit message.

    :param lines: Commit messsage lines
    :param cls: `MessageValidator` class
    :return: Sorted list of validation errors
    """
    validator = cls()
    errors = list(validator.validate(lines))
    errors.sort(key=operator.attrgetter("rule_id"))
    errors.sort(key=operator.attrgetter("lineno"))
    return errors


def check_message(lines, validator_cls=GerritMessageValidator):
    """
    Check a commit message to see if it has errors.

    This method will check the commit message by using an appropriate checker
    depending on what remote repo is.

    :param lines:
        list of lines from the commit message that will be checked.
    :param validator_cls:
        A class that implements `MessageValidator` class,
        default to `GerritMessageValidator`.
    :return:
        An integer, used for exit code.
    """
    print("commit-message-validator")
    print(
        "Using {} to check the commit message".format(
            validator_cls.__name__,
        ),
    )
    errors = lint_message(lines, validator_cls)
    if errors:
        color, reset = ansi_codes()
        print(f"{color}The following errors were found:{reset}")
        for err in errors:
            print(f"{color}Line {err.lineno}: {err.message}{reset}")
        if validator_cls is GerritMessageValidator:
            print(
                "{}{}{}".format(
                    color,
                    GERRIT_CHECK_FAIL_MESSAGE_SUGGESTION,
                    reset,
                ),
            )
        return 1
    else:
        print("Commit message is formatted properly! Keep up the good work!")
    return 0


def validate(commit_id="HEAD", validator=None):
    """Validate the current HEAD commit message."""
    # First, we need to check if HEAD is a merge commit
    # We do this by telling if it has multiple parents
    parents = (
        check_output(
            "git",
            "log",
            "--format=%P",
            commit_id,
            "-n1",
        )
        .strip()
        .split(" ")
    )
    if len(parents) > 1:
        # Use the right-most parent
        commit_id = parents[-1]

    commit = check_output(
        "git",
        "log",
        "--format=%B",
        "--no-color",
        commit_id,
        "-n1",
    )
    lines = commit.splitlines()
    # last line is sometimes an empty line
    if len(lines) > 0 and not lines[-1]:
        lines = lines[:-1]

    if validator and type(validator) == str:
        validator = {
            "GerritMessageValidator": GerritMessageValidator,
            "GitHubMessageValidator": GitHubMessageValidator,
            "GitLabMessageValidator": GitLabMessageValidator,
        }.get(validator)
    if validator is None:
        validator = guess_message_validator_class()
    return check_message(lines, validator)


def sample(repo, count):
    """Sample commits from a given repo."""
    os.chdir(repo)
    sha1s = check_output(
        "git",
        "log",
        "--format=%H",
        "--no-merges",
        f"-n{count}",
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
    print(f"{bad/(bad+good):.2%} commits failed validation.")
