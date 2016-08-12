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

__version__ = '0.3.1'


def line_errors(lineno, line):
    """Check a commit message line to see if it has errors.

    Checks:
    - First line <=80 characters
    - Second line blank
    - No line >100 characters (unless it is only a URL)
    - "Bug:" is capitalized
    - "Bug:" is followed by a space
    - Exactly one task id on each Bug: line
    - "Depends-On:" is capitalized
    - "Depends-On:" is followed by a space
    - Exactly one change id on each Depends-On: line
    - No "Task: ", "Fixes: ", "Closes: " lines
    """
    # First line <=80
    if lineno == 0:
        if len(line) > 80:
            yield "First line should be <=80 characters"
        m = re.match(r'^T?\d+', line, re.IGNORECASE)
        if m:
            yield "Do not define bug in the header"

    # Second line blank
    elif lineno == 1:
        if line:
            yield "Second line should be empty"

    # No line >100 unless it is all a URL
    elif len(line) > 100:
        m = re.match(r'^<?https?://\S+>?$', line, re.IGNORECASE)
        if not m:
            yield "Line should be <=100 characters"

    m = re.match(r'^(bug|closes|fixes|task):(\W)*(.*)', line, re.IGNORECASE)
    if m:
        if lineno == 0:
            yield "Do not define bug in the header"

        if m.group(1).lower() == 'bug':
            if m.group(1) != 'Bug':
                yield "Expected 'Bug:' not '%s:'" % m.group(1)
        else:
            # No "Task: ", "Fixes: ", "Closes: " lines
            yield "Use 'Bug: ' not '%s:'" % m.group(1)

        if m.group(2) != ' ':
            yield "Expected one space after 'Bug:'"

        bug_id = m.group(3).strip()
        if bug_id.isdigit():
            yield "The bug ID must be a phabricator task ID"
        elif bug_id.upper().startswith('T') and bug_id[1:].isdigit():
            if bug_id[0] != 'T':
                assert bug_id[0] == 't'
                yield "The phabricator task ID must use uppercase T"
        else:
            yield "The bug ID is not a phabricator task ID"

    m = re.match(r'^(depends-on):(\W)*(.*)', line, re.IGNORECASE)
    if m:
        if lineno == 0:
            yield "Do not define dependency in the header"

        if m.group(1) != 'Depends-On':
            yield "Expected 'Depends-On' not '%s:'" % m.group(1)

        if m.group(2) != ' ':
            yield "Expected one space after 'Depends-On:'"

        change_id = m.group(3).strip()
        change_id_is_hex = True
        try:
            int(change_id[1:], 16)
        except ValueError:
            change_id_is_hex = False
        if change_id.upper().startswith('I') and change_id_is_hex:
            if change_id[0] != 'I':
                yield "The Depends-On value must use uppercase I"
        else:
            yield "The Depends-On value is not a Gerrit Change-Id"


def check_message(lines):
    """Check a commit message to see if it has errors.

    Checks:
    - All lines ok as checked by line_errors()
    - For any "^Bug: " line, next line is not blank
    - For any "^Bug: " line, prior line is another Bug: line or empty
    - For any "^Depends-On: " line, next line is not blank
    - For any "^Depends-On: " line, prior line is Bug|Depends-On or empty
    - Exactly one "Change-Id: " line per commit
    - For "Change-Id: " line, prior line is empty or "^(Bug|Depends-On): "
    - No blank lines between any "(Bug|Depends-On): " lines and "Change-Id: "
    - Only "(cherry picked from commit" can follow "Change-Id: "
    - Message has at least 3 lines (subject, blank, Change-Id)
    """
    errors = []
    last_lineno = 0
    last_line = ''
    changeid_line = False
    last_bug = False
    last_depends = False
    for lineno, line in enumerate(lines):
        rline = lineno + 1
        errors.extend('Line {0}: {1}'.format(rline, e)
                      for e in line_errors(lineno, line))

        # For any "Bug: " line, next line is not blank
        if last_bug == last_lineno:
            if not line:
                errors.append(
                    "Line %d: Unexpected blank line after Bug:" % rline)

        # For any "Depends-On: " line, next line is not blank
        if last_depends == last_lineno:
            if not line:
                errors.append(
                    "Line %d: Unexpected blank line after Depends-On:" % rline)

        # For any "Bug: " line, prior line is another Bug: line or empty
        if line.startswith('Bug: '):
            last_bug = rline
            if last_line and not last_line.startswith('Bug: '):
                errors.append(
                    "Line %d: Expected blank line before Bug:" % rline)

        # For any "Depends-On: " line, prior line is Bug, Depends-On, or empty
        if line.startswith('Depends-On: '):
            last_depends = rline
            if last_line and not (
                last_line.startswith('Bug: ') or
                last_line.startswith('Depends-On: ')
            ):
                errors.append(
                    "Line %d: Expected blank line before Depends-On:" % rline)

        if line.startswith('Change-Id: I'):
            # Only expect one "Change-Id: " line
            if changeid_line is not False:
                errors.append(
                    "Line %d: Extra Change-Id found, next at %d" %
                    (changeid_line, rline))

            # For "Change-Id: " line, prior line is empty or Bug:
            elif last_line and not (
                last_line.startswith('Bug: ') or
                last_line.startswith('Depends-On: ')
            ):
                errors.append(
                    "Line %d: Expected blank line, Bug:, "
                    "or Depends-On: before Change-Id:" % rline)

            # If we have Bug|Depends-On: lines, Change-Id follows immediately
            elif last_bug or last_depends and (
                max(last_bug, last_depends) != rline - 1
            ):
                lookback = max(last_bug, last_depends)
                label = "Bug:" if lookback == last_bug else "Depends-On:"

                for lno in range(lookback + 1, rline):
                    errors.append(
                        "Line %d: Unexpected line between %s and Change-Id:"
                        % (lno, label))

            changeid_line = rline

        last_lineno = rline
        last_line = line

    if last_lineno < 2:
        errors.append("Line %d: Expected at least 3 lines" % last_lineno)

    if changeid_line is False:
        errors.append("Line %d: Expected Change-Id" % last_lineno)

    elif changeid_line != last_lineno:
        if last_lineno != changeid_line + 1:
            for lno in range(changeid_line + 1, last_lineno):
                errors.append(
                    "Line %d: Unexpected line after Change-Id" % lno)
        if not last_line.startswith("(cherry picked from commit"):
            errors.append(
                "Line %d: Unexpected line after Change-Id" % last_lineno)

    print('commit-message-validator v%s' % __version__)
    if errors:
        print('The following errors were found:')
        for e in errors:
            print(e)
        print('Please review <https://www.mediawiki.org/wiki/Gerrit/Commit_message_guidelines>'
              ' and update your commit message accordingly')
        return 1
    else:
        print('Commit message is formatted properly! Keep up the good work!')
    return 0


def check_output(args):
    """Wrapper around subprocess to handle Python 3"""
    return subprocess.check_output(args).decode()


def main():
    """Validate the current HEAD commit message."""
    # First, we need to check if HEAD is a merge commit
    # We do this by telling if it has multiple parents
    parents = check_output(
        ['git', 'log', '--format=%P', 'HEAD', '-n1']
    ).strip().split(' ')
    if len(parents) > 1:
        # Use the right-most parent
        commit_id = parents[-1]
    else:
        commit_id = 'HEAD'

    commit = check_output(
        ['git', 'log', '--format=%B', '--no-color', commit_id, '-n1'])
    # last line is always an empty line
    lines = commit.splitlines()[:-1]

    return check_message(lines)

if __name__ == '__main__':
    import sys
    sys.exit(main())
