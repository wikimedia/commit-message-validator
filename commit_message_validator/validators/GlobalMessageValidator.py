import re

from commit_message_validator.message_validator import MessageValidator

RE_URL = re.compile(r'^<?https?://\S+>?$', re.IGNORECASE)
RE_REVERT_SUBJECT = re.compile('^Revert ".*"$')


class GlobalMessageValidator(MessageValidator):
    """
    An iterator to validate all remote repo commit message.

    Checks:
    - First line <=80 characters or /^Revert ".*"$/
    - Second line blank
    - No line >100 characters (unless it is only a URL)

    Global checks:
    - At least 3 lines in a commit message
    """

    def check_line(self, lineno):
        line = self._lines[lineno]

        # First line <=80
        if lineno == 0 and len(line) > 80:
            if not RE_REVERT_SUBJECT.match(line):
                yield "First line should be <=80 characters"

        # Second line blank
        elif lineno == 1 and line:
            yield "Second line should be empty"

        # No line >100 characters (unless it is only a URL)
        elif len(line) > 100 and not RE_URL.match(line):
            yield "Line should be <=100 characters"

    def check_global(self):
        # At least 3 lines in a commit message
        if len(self._lines) < 3:
            yield "Expected at least 3 lines"
