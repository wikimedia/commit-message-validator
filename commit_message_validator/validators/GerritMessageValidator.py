import re

from .GlobalMessageValidator import GlobalMessageValidator

RE_CHERRYPICK = re.compile(r'^\(cherry picked from commit [0-9a-fA-F]{40}\)$')
RE_GERRIT_CHANGEID = re.compile('^I[a-f0-9]{40}$')
RE_GERRIT_FOOTER = re.compile(
    r'^(?P<name>[a-z]\S+):(?P<ws>\s*)(?P<value>.*)$', re.IGNORECASE)
RE_PHABRICATOR_BUGID = re.compile('^T[0-9]+$')
RE_SUBJECT_BUG_OR_TASK = re.compile(r'^(bug|T?\d+)', re.IGNORECASE)

# Header-like lines that we are interested in validating
CORRECT_FOOTERS = [
    'Acked-by',
    'Bug',
    'Cc',
    'Change-Id',
    'Co-Authored-by',
    'Depends-On',
    'Hosts',  # Wikimedia puppet-compiler
    'Requested-by',
    'Reported-by',
    'Reviewed-by',
    'Signed-off-by',
    'Suggested-by',
    'Tested-by',
    'Thanks',
]
FOOTERS = dict((footer.lower(), footer) for footer in CORRECT_FOOTERS)

BEFORE_CHANGE_ID = [
    'bug',
    'closes',
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
    return RE_PHABRICATOR_BUGID.match(s)


def is_valid_change_id(s):
    """A Gerrit change id is a 40 character hex string prefixed with 'I'."""
    return RE_GERRIT_CHANGEID.match(s)


class CommitMessageContext(object):
    HEADER = 1
    BODY = 2
    FOOTER = 3


class GerritMessageValidator(GlobalMessageValidator):
    """
    An iterator to validate Gerrit remote repo commit message.

    Checks:
    - First line <=80 characters or /^Revert ".*"$/
    - Second line blank
    - No line >100 characters (unless it is only a URL)
    - Footer lines ("Foo: ...") are capitalized and have a space after the ':'
    - "Bug: " is followed by one task id ("Tnnnn")
    - "Depends-On:" is followed by one change id ("I...")
    - "Change-Id:" is followed one change id ("I...")
    - No "Task: ", "Fixes: ", "Closes: " lines
    """

    def __init__(self, lines):
        """
        MessageValidator for Gerrit remote origin.

        :param lines: list of lines from the commit message that will be
                      checked.
        """
        super(GerritMessageValidator, self).__init__(lines)

        self._commit_message_context = None
        self._first_changeid = False

    def check_line(self, lineno):
        for error in super(GerritMessageValidator, self).check_line(lineno):
            yield error

        line_context = self.get_context(lineno)
        line = self._lines[lineno]

        if (line_context is CommitMessageContext.HEADER and
                RE_SUBJECT_BUG_OR_TASK.match(line)):
            yield "Do not define bug in the header"

        if (not line and
                line_context is CommitMessageContext.FOOTER):
            yield "Unexpected blank line"

        gerrit_footer_match = RE_GERRIT_FOOTER.match(line)
        if gerrit_footer_match:
            name = gerrit_footer_match.group('name')
            normalized_name = name.lower()
            ws = gerrit_footer_match.group('ws')
            value = gerrit_footer_match.group('value')

            if normalized_name in BAD_FOOTERS:
                # Treat as the correct name for the rest of the rules
                normalized_name = BAD_FOOTERS[normalized_name]

            if normalized_name not in FOOTERS:
                if line_context is CommitMessageContext.FOOTER:
                    yield "Unexpected line in footers"
                else:
                    # Meh. Not a name we care about
                    return
            elif (line_context is not
                    CommitMessageContext.FOOTER):
                yield "Expected '{0}:' to be in footer".format(name)

            correct_name = FOOTERS.get(normalized_name)
            if correct_name and correct_name != name:
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

        elif (line and
              line_context is CommitMessageContext.FOOTER):
            # if it wasn't a footer (not a match) but it is in the footers
            cherry_pick = RE_CHERRYPICK.match(line)
            if cherry_pick:
                if lineno < len(self._lines) - 1:
                    yield "Cherry pick line is not the last line"
            else:
                yield "Expected footer line to follow format of 'Name: ...'"

    def check_global(self):
        for error in super(GerritMessageValidator, self).check_global():
            yield error

        if self._first_changeid is False:
            yield "Expected Change-Id"

    def get_context(self, lineno):
        """
        Get the context of the current line.

        :param lineno: Line number that the context will be checked.
        :return:       A `CommitMessageContext` enum.
        """
        if lineno == 0:
            # First line in the commit message is HEADER.
            self._commit_message_context = CommitMessageContext.HEADER
        elif self._commit_message_context is not CommitMessageContext.FOOTER:
            line = self._lines[lineno]
            footer_match = RE_GERRIT_FOOTER.match(line)
            cherrypick_match = RE_CHERRYPICK.match(line)

            if (((footer_match and
                  footer_match.group('name').lower() in FOOTERS)
                 or cherrypick_match) and
                    not self._lines[lineno - 1]):
                # If the current line is a footer ("Name: ..." formatted)
                # and it's indeed a footer (the "Name" listed in the FOOTERS)
                # or it's a cherry pick
                # and the previous line is a blank line.
                # Mark the current line until the end as FOOTER.
                self._commit_message_context = CommitMessageContext.FOOTER
            else:
                self._commit_message_context = CommitMessageContext.BODY

        return self._commit_message_context
