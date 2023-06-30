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
Validate the format of a commit message to Wikimedia Gerrit standards.

https://www.mediawiki.org/wiki/Gerrit/Commit_message_guidelines
"""
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


def get_message_validator_class():
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
    validator = validator_cls()
    errors = list(validator.validate(lines))
    errors.sort(key=operator.attrgetter("rule_id"))
    errors.sort(key=operator.attrgetter("lineno"))

    print("commit-message-validator")
    print(
        "Using {} to check the commit message".format(
            validator_cls.__name__,
        ),
    )
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


def validate(commit_id="HEAD"):
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
    else:
        commit_id = commit_id

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

    return check_message(lines, get_message_validator_class())


def install():
    """Install post-commit git hook."""
    cmd = sys.executable + " " + __file__
    if os.name == "nt":  # T184845
        cmd = cmd.replace("\\", "/")
    print("Will install a git hook that runs: %s" % cmd)
    git_dir = check_output("git", "rev-parse", "--git-dir").strip()
    path = os.path.join(git_dir, "hooks", "post-commit")
    if os.path.exists(path):
        # Check to see if it's already installed
        with open(path) as f:
            contents = f.read()
        if (
            "commit-message-validator" in contents
            or "commit_message_validator" in contents
        ):
            print("commit-message-validator git hook is already installed")
            return 1
        # Not installed, but hook already exists.
        with open(path, "a") as f:
            f.write("\n" + cmd + "\n")
        print("Installed commit-message-validator in %s" % path)
        return 0
    # Doesn't exist, we need to create a hook and make it +x
    with open(path, "w") as f:
        f.write("#!/bin/sh\n" + cmd + "\n")
    check_output("chmod", "+x", path)
    return 0


def main():
    if sys.argv[-1] == "install":
        sys.exit(install())
    else:
        sys.exit(validate())


if __name__ == "__main__":  # pragma: nocover
    main()
