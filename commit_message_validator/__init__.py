#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Validate the format of a commit message to Wikimedia Gerrit standards.

https://www.mediawiki.org/wiki/Gerrit/Commit_message_guidelines

Copyright (C) 2015 Bryan Davis and Wikimedia Foundation

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
from __future__ import print_function

import os
import subprocess
import sys

from commit_message_validator.validators.GerritMessageValidator import (
    GerritMessageValidator)

__version__ = '0.5.2'


def check_message(lines):
    """Check a commit message to see if it has errors.

    Checks:
    - All lines ok as checked by line_errors()
    - Message has at least 3 lines (subject, blank, Change-Id)
    - For any footer line, next line is not blank
    - For any footer line, prior line is another footer line or blank
    - Exactly one "Change-Id: " line per commit
    - Any "Bug:" and "Depends-On:" lines come before "Change-Id:"
    - "(cherry picked from commit ...)" is last line in footer if present
    """
    validator = GerritMessageValidator(lines)
    errors = ["Line {0}: {1}".format(lineno, error)
              for lineno, error in validator]

    print('commit-message-validator v%s' % __version__)
    if errors:
        print('The following errors were found:')
        for e in errors:
            print(e)
        print(
            'Please review '
            '<https://www.mediawiki.org/wiki/Gerrit/Commit_message_guidelines>'
            '\nand update your commit message accordingly')
        return 1
    else:
        print('Commit message is formatted properly! Keep up the good work!')
    return 0


def check_output(args):
    """Wrapper around subprocess to handle Python 3"""
    return subprocess.check_output(args).decode("utf8")


def validate(commit_id='HEAD'):
    """Validate the current HEAD commit message."""
    # First, we need to check if HEAD is a merge commit
    # We do this by telling if it has multiple parents
    parents = check_output(
        ['git', 'log', '--format=%P', commit_id, '-n1']
    ).strip().split(' ')
    if len(parents) > 1:
        # Use the right-most parent
        commit_id = parents[-1]
    else:
        commit_id = commit_id

    commit = check_output(
        ['git', 'log', '--format=%B', '--no-color', commit_id, '-n1'])
    lines = commit.splitlines()
    # last line is sometimes an empty line
    if len(lines) > 0 and not lines[-1]:
        lines = lines[:-1]

    return check_message(lines)


def install():
    """Install post-commit git hook."""
    cmd = sys.executable + ' ' + __file__
    if os.name == 'nt':  # T184845
        cmd = cmd.replace('\\', '/')
    print('Will install a git hook that runs: %s' % cmd)
    git_dir = check_output(['git', 'rev-parse', '--git-dir']).strip()
    path = os.path.join(git_dir, 'hooks', 'post-commit')
    if os.path.exists(path):
        # Check to see if it's already installed
        with open(path) as f:
            contents = f.read()
        if 'commit-message-validator' in contents or 'commit_message_validator' in contents:
            print('commit-message-validator git hook is already installed')
            return 1
        # Not installed, but hook already exists.
        with open(path, 'a') as f:
            f.write('\n' + cmd + '\n')
        print('Installed commit-message-validator in %s' % path)
        return 0
    # Doesn't exist, we need to create a hook and make it +x
    with open(path, 'w') as f:
        f.write(cmd + '\n')
    subprocess.check_call(['chmod', '+x', path])
    return 0


def main():
    if sys.argv[-1] == 'install':
        sys.exit(install())
    else:
        sys.exit(validate())


if __name__ == '__main__':
    main()
