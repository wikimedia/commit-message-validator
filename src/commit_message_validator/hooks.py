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
import os
import sys

from .utils import check_output


def install():
    """Install post-commit git hook."""
    cmd = sys.executable + " -m commit_message_validator validate"
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
