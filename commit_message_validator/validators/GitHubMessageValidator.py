import re

from commit_message_validator.validators.GlobalMessageValidator import (
    GlobalMessageValidator)

RE_GITHUB_ISSUE_NUMBER = re.compile(r'#\d+')
RE_GITHUB_CLOSE_ISSUE_IN_DIFFERENT_REPO = re.compile(
    r'^(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+\S+/\S+#\d+',
    re.IGNORECASE
)


class GitHubMessageValidator(GlobalMessageValidator):
    """
    An iterator to validate GitHub remote repo commit message.

    Checks:
    - First line <=80 characters or /^Revert ".*"$/
    - Second line blank
    - No line >100 characters (unless it is only a URL)
    - Issue should not be defined in the header
    - "Closing issue keywords" for closing an issue that is in another
    repository shouldn't be exist.
    """

    def check_line(self, lineno):
        for error in super(GitHubMessageValidator, self).check_line(lineno):
            yield error

        line = self._lines[lineno]

        if lineno == 0 and RE_GITHUB_ISSUE_NUMBER.findall(line):
            yield "Do not define bug in the header"

        if RE_GITHUB_CLOSE_ISSUE_IN_DIFFERENT_REPO.match(line):
            yield (
                'Do not write "closing issue keywords" for closing an issue '
                'that is in another repository')
