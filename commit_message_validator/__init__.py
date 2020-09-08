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
from commit_message_validator.validators.GitHubMessageValidator import (
    GitHubMessageValidator)

__version__ = '0.7.0'


WIKIMEDIA_GERRIT_URL = 'gerrit.wikimedia.org'
GERRIT_CHECK_FAIL_MESSAGE_SUGGESTION = (
    'Please review '
    '<https://www.mediawiki.org/wiki/Gerrit/Commit_message_guidelines>'
    '\nand update your commit message accordingly')


def get_message_validator_class():
    """
    Get appropriate MessageValidator class to check the commit message
    in the repo.

    This method will check whether the remote repo is a Gerrit or GitHub, and
    return the appropriate MessageValidator class to check the commit message.

    :return: A class that implements `MessageValidator` class.
    """
    result = None
    if os.path.exists('.gitreview') and os.path.isfile('.gitreview'):
        result = check_output(
            ['git', 'config', '-f', '.gitreview', '--get', 'gerrit.host'])

    if result and WIKIMEDIA_GERRIT_URL in result:
        return GerritMessageValidator
    else:
        result = check_output(
            ['git', 'config', '--get-regex', '^remote.*.url$'])

        remotes = result.splitlines()
        remote_dict = dict()

        for remote in remotes:
            remote_splitted = remote.split(' ')
            remote_dict[remote_splitted[0]] = remote_splitted[1]

        if (WIKIMEDIA_GERRIT_URL in {remote_dict.get('remote.wikimedia.url'),
                                     remote_dict.get('remote.gerrit.url')}):
            return GerritMessageValidator
        elif 'github.com' in remote_dict.get('remote.origin.url'):
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
    errors = ["Line {0}: {1}".format(lineno, error)
              for lineno, error in validator_cls(lines)]

    print('commit-message-validator v%s' % __version__)
    print('Using {0} to check the commit message'.format(
        validator_cls.__name__))
    if errors:
        color, reset = ansi_codes()
        print('{}The following errors were found:{}'.format(color, reset))
        for e in errors:
            print("{}{}{}".format(color, e, reset))
        if validator_cls is GerritMessageValidator:
            print("{}{}{}".format(
                color, GERRIT_CHECK_FAIL_MESSAGE_SUGGESTION, reset))
        return 1
    else:
        print('Commit message is formatted properly! Keep up the good work!')
    return 0


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
    stdout_is_tty = 'true' if sys.stdout.isatty() else 'false'
    try:
        # Ask git if colors should be used
        # Raises CalledProcessError if disabled
        subprocess.check_output([
            'git', 'config', '--get-colorbool',
            'color.commit_message_validator', stdout_is_tty
        ])
        # Get configured color code (default to red text)
        return check_output([
            'git', 'config', '--get-color',
            'color.commit_message_validator.error', 'red'
        ]), '\x1b[0m'
    except subprocess.CalledProcessError:
        return '', ''


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

    return check_message(lines, get_message_validator_class())


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
        f.write('#!/bin/sh\n' + cmd + '\n')
    subprocess.check_call(['chmod', '+x', path])
    return 0


def main():
    if sys.argv[-1] == 'install':
        sys.exit(install())
    else:
        sys.exit(validate())


if __name__ == '__main__':
    main()
