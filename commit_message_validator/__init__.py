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

import re
import subprocess


def line_errors(lineno, line):
    """Check a commit message line to see if it has errors.

    Checks:
    - First line <=80 characters
    - Second line blank
    - No line >100 characters
    - "Bug:" is capitalized
    - "Bug:" is followed by a space
    - Exactly one task id on each Bug: line
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

    # No line >100
    elif len(line) > 100:
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


def check_message(lines):
    """Check a commit message to see if it has errors.

    Checks:
    - All lines ok as checked by line_errors()
    - For any "^Bug: " line, next line is not blank
    - For any "^Bug: " line, prior line is another Bug: line or empty
    - Exactly one "Change-Id: " line per commit
    - For "Change-Id: " line, prior line is empty or "^Bug: "
    - No blank lines between any "Bug: " lines and "Change-Id: "
    - Only "(cherry picked from commit" can follow "Change-Id: "
    - Message has at least 3 lines (subject, blank, Change-Id)
    """
    errors = []
    last_lineno = 0
    last_line = ''
    changeid_line = False
    last_bug = False
    for lineno, line in enumerate(lines):
        rline = lineno + 1
        errors.extend('Line {0}: {1}'.format(rline, e)
                      for e in line_errors(lineno, line))

        # For any "Bug: " line, next line is not blank
        if last_bug == last_lineno:
            if not line:
                errors.append(
                    "Line %d: Unexpected blank line after Bug:" % rline)

        # For any "Bug: " line, prior line is another Bug: line or empty
        if line.startswith('Bug: '):
            last_bug = rline
            if last_line and not last_line.startswith('Bug: '):
                errors.append(
                    "Line %d: Expected blank line before Bug:" % rline)

        if line.startswith('Change-Id: I'):
            # Only expect one "Change-Id: " line
            if changeid_line is not False:
                errors.append(
                    "Line %d: Extra Change-Id found, next at %d" %
                    (changeid_line, rline))

            # For "Change-Id: " line, prior line is empty or Bug:
            elif last_line and not last_line.startswith('Bug: '):
                errors.append(
                    "Line %d: Expected blank line or Bug: before Change-Id:" %
                    rline)

            # If we have Bug: lines, Change-Id follows immediately
            elif last_bug and last_bug != rline - 1:
                for lno in range(last_bug + 1, rline):
                    errors.append(
                        "Line %d: Unexpected line between Bug: and Change-Id:"
                        % lno)

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

    if errors:
        for e in errors:
            print(e)
        return 1
    return 0


def main():
    """Validate the current HEAD commit message."""
    commit = subprocess.check_output(
        ['git', 'log', '--format=%B', '--no-color', '-n1'])
    # last line is always an empty line
    lines = commit.splitlines()[:-1]

    return check_message(lines)

if __name__ == '__main__':
    import sys
    sys.exit(main())
