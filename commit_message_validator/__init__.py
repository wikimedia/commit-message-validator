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

import re
import subprocess
import sys

__version__ = '0.4.1'

RE_BUGID = re.compile('^T[0-9]+$')
RE_CHANGEID = re.compile('^I[a-f0-9]{40}$')
RE_SUBJECT_BUG_OR_TASK = re.compile(r'^(bug|T?\d+)', re.IGNORECASE)
RE_URL = re.compile(r'^<?https?://\S+>?$', re.IGNORECASE)
RE_FOOTER = re.compile(
    r'^(?P<name>[a-z]\S+):(?P<ws>\s*)(?P<value>.*)$', re.IGNORECASE)
RE_CHERRYPICK = re.compile(r'^\(cherry picked from commit [0-9a-fA-F]{40}\)$')

# Header-like lines that we are interested in validating
FOOTERS = [
    'acked-by',
    'bug',
    'cc',
    'change-id',
    'closes',
    'co-authored-by',
    'depends-on',
    'fixes',
    'reported-by',
    'reviewed-by',
    'signed-off-by',
    'suggested-by',
    'task',
    'tested-by',
    'thanks',
]

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


def line_errors(lineno, line):
    """Check a commit message line to see if it has errors.

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
    if len(line) > 100 and not RE_URL.match(line):
        yield "Line should be <=100 characters"

    # Look for and validate footer lines
    m = RE_FOOTER.match(line)
    if m:
        name = m.group('name')
        normalized_name = name.lower()
        ws = m.group('ws')
        value = m.group('value')

        if normalized_name not in FOOTERS:
            # Meh. Not a name we care about
            raise StopIteration

        if normalized_name in BAD_FOOTERS:
            # Treat as the correct name for the rest of the rules
            normalized_name = BAD_FOOTERS[normalized_name]

        if normalized_name == 'bug':
            if name != 'Bug':
                yield "Use 'Bug:' not '{0}:'".format(name)
            if not is_valid_bug_id(value):
                yield "Bug: value must be a single phabricator task ID"

        elif normalized_name == 'depends-on':
            if name != 'Depends-On':
                yield "Use 'Depends-On:' not '%s:'" % name
            if not is_valid_change_id(value):
                yield "Depends-On: value must be a single Gerrit change id"

        elif normalized_name == 'change-id':
            if name != 'Change-Id':
                yield "Use 'Change-Id:' not '%s:'" % name
            if not is_valid_change_id(value):
                yield "Change-Id: value must be a single Gerrit change id"

        elif name[0].upper() != name[0]:
            yield "'%s:' must start with a capital letter" % name

        if ws != ' ':
            yield "Expected one space after '%s:'" % name


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
    errors = []
    last_lineno = 0
    last_line = ''
    changeid_line = False
    cherrypick_line = False
    in_footer = False

    for lineno, line in enumerate(lines):
        rline = lineno + 1
        errors.extend('Line {0}: {1}'.format(rline, e)
                      for e in line_errors(lineno, line))

        if in_footer:
            if line == '':
                errors.append(
                    "Line {0}: Unexpected blank line".format(rline))
            elif not (RE_FOOTER.match(line) or RE_CHERRYPICK.match(line)):
                errors.append((
                    "Line {0}: Expected footer line to follow format of "
                    "'Name: ...'").format(rline))

        m = RE_FOOTER.match(line)
        if m:
            name = m.group('name')
            normalized_name = name.lower()

            if last_line == '' and normalized_name in FOOTERS:
                # The first footer after a blank line starts the footer
                in_footer = True

            if normalized_name in FOOTERS and not in_footer:
                errors.append(
                    "Line {0}: Expected '{1}:' to be in footer".format(
                        rline, name))

            if normalized_name == 'change-id':
                # Only expect one "Change-Id: " line
                if changeid_line is not False:
                    errors.append(
                        "Line {0}: Extra Change-Id found, first at {1}".format(
                            rline, changeid_line))
                changeid_line = rline

            elif normalized_name in BEFORE_CHANGE_ID:
                if changeid_line is not False:
                    errors.append((
                        "Line {0}: Expected '{1}:' to come before "
                        "Change-Id on line {2}").format(
                            rline, name, changeid_line))

        elif RE_CHERRYPICK.match(line):
            cherrypick_line = rline

        last_lineno = rline
        last_line = line

    if last_lineno < 2:
        errors.append("Line %d: Expected at least 3 lines" % last_lineno)

    if changeid_line is False:
        errors.append("Line %d: Expected Change-Id" % last_lineno)

    if cherrypick_line and cherrypick_line != last_lineno:
        errors.append(
            "Line {0}: Cherry pick expected to be last line".format(
                cherrypick_line))

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
    return subprocess.check_output(args).decode()


def main(commit_id='HEAD'):
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
    # last line is always an empty line
    lines = commit.splitlines()[:-1]

    return check_message(lines)

if __name__ == '__main__':
    sys.exit(main())
