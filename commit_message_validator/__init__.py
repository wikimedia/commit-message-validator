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
import re
import subprocess
import sys

__version__ = '0.5.1'

RE_BUGID = re.compile('^T[0-9]+$')
RE_CHANGEID = re.compile('^I[a-f0-9]{40}$')
RE_SUBJECT_BUG_OR_TASK = re.compile(r'^(bug|T?\d+)', re.IGNORECASE)
RE_URL = re.compile(r'^<?https?://\S+>?$', re.IGNORECASE)
RE_FOOTER = re.compile(
    r'^(?P<name>[a-z]\S+):(?P<ws>\s*)(?P<value>.*)$', re.IGNORECASE)
RE_CHERRYPICK = re.compile(r'^\(cherry picked from commit [0-9a-fA-F]{40}\)$')

# Header-like lines that we are interested in validating
CORRECT_FOOTERS = [
    'Acked-By',
    'Bug',
    'Cc',
    'Change-Id',
    'Co-Authored-By',
    'Depends-On',
    'Reported-By',
    'Reviewed-by',
    'Signed-off-by',
    'Suggested-By',
    'Tested-by',
    'Thanks',
]
FOOTERS = dict((footer.lower(), footer) for footer in CORRECT_FOOTERS)

BEFORE_CHANGE_ID = [
    'bug',
    'closes',
    'depends-on',
    'fixes',
    'task',
]

# Invalid footer name to expected name mapping
BAD_FOOTERS = {
    'closes': 'bug',
    'fixes': 'bug',
    'task': 'bug',
}


def is_valid_bug_id(s):
    return RE_BUGID.match(s)


def is_valid_change_id(s):
    """A Gerrit change id is a 40 character hex string prefixed with 'I'."""
    return RE_CHANGEID.match(s)


class MessageValidator(object):

    """Iterator to check a commit message line for errors.

    Checks:
    - First line <=80 characters
    - Second line blank
    - No line >100 characters (unless it is only a URL)
    - Footer lines ("Foo: ...") are capitalized and have a space after the ':'
    - "Bug: " is followed by one task id ("Tnnnn")
    - "Depends-On:" is followed by one change id ("I...")
    - "Change-Id:" is followed one change id ("I...")
    - No "Task: ", "Fixes: ", "Closes: " lines
    """

    def __init__(self, lines):
        self._lines = lines
        self._first_changeid = False
        self._in_footers = False

        self._generator = self._check_generator()

    def _check_line(self, lineno):
        line = self._lines[lineno]
        # First line <=80
        if lineno == 0:
            if len(line) > 80:
                yield "First line should be <=80 characters"
            m = RE_SUBJECT_BUG_OR_TASK.match(line)
            if m:
                yield "Do not define bug in the header"

        # Second line blank
        elif lineno == 1:
            if line:
                yield "Second line should be empty"

        # No line >100 unless it is all a URL
        elif len(line) > 100 and not RE_URL.match(line):
            yield "Line should be <=100 characters"

        if not line:
            if self._in_footers:
                yield "Unexpected blank line"
            return

        # Look for and validate footer lines
        m = RE_FOOTER.match(line)
        if m:
            name = m.group('name')
            normalized_name = name.lower()
            ws = m.group('ws')
            value = m.group('value')

            if normalized_name in BAD_FOOTERS:
                # Treat as the correct name for the rest of the rules
                normalized_name = BAD_FOOTERS[normalized_name]

            if normalized_name not in FOOTERS:
                if self._in_footers:
                    yield "Unexpected line in footers"
                else:
                    # Meh. Not a name we care about
                    return
            else:
                if lineno > 0 and not self._lines[lineno - 1]:
                    self._in_footers = True
                elif not self._in_footers:
                    yield "Expected '{0}:' to be in footer".format(name)

            correct_name = FOOTERS[normalized_name]
            if correct_name != name:
                yield "Use '{0}:' not '{1}:'".format(correct_name, name)

            if normalized_name == 'bug':
                if not is_valid_bug_id(value):
                    yield "Bug: value must be a single phabricator task ID"

            elif normalized_name == 'depends-on':
                if not is_valid_change_id(value):
                    yield "Depends-On: value must be a single Gerrit change id"

            elif normalized_name == 'change-id':
                if not is_valid_change_id(value):
                    yield "Change-Id: value must be a single Gerrit change id"
                if self._first_changeid is not False:
                    yield ("Extra Change-Id found, first at "
                           "{0}".format(self._first_changeid))
                else:
                    self._first_changeid = lineno + 1

            if (normalized_name in BEFORE_CHANGE_ID and
                    self._first_changeid is not False):
                yield ("Expected '{0}:' to come before Change-Id on line "
                       "{1}").format(name, self._first_changeid)

            if ws != ' ':
                yield "Expected one space after '%s:'" % name

        elif self._in_footers:
            # if it wasn't a footer (not a match) but it is in the footers
            cherry_pick = RE_CHERRYPICK.match(line)
            if cherry_pick:
                if lineno < len(self._lines) - 1:
                    yield "Cherry pick line is not the last line"
            else:
                yield "Expected footer line to follow format of 'Name: ...'"

    def _check_global(self):
        """All checks that are done after the line checks."""
        if len(self._lines) < 3:
            yield "Expected at least 3 lines"

        if self._first_changeid is False:
            yield "Expected Change-Id"

    def _check_generator(self):
        """A generator returning each error and line number."""
        for lineno in range(len(self._lines)):
            for e in self._check_line(lineno):
                yield lineno + 1, e

        for e in self._check_global():
            yield len(self._lines), e

    def __iter__(self):
        return self

    def __next__(self):
        """Return the next error of the generator."""
        return next(self._generator)

    def next(self):
        # For Python 2 support
        return self.__next__()


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
    validator = MessageValidator(lines)
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
