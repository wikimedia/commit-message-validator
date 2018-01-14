#!/usr/bin/env python

import os
from six import with_metaclass
import sys
import unittest

import commit_message_validator as cmv

from commit_message_validator.validators.GerritMessageValidator import (
    GerritMessageValidator
)
from commit_message_validator.validators.GitHubMessageValidator import (
    GitHubMessageValidator
)

if sys.version_info[0] > 2:
    from io import StringIO
else:
    from StringIO import StringIO


MESSAGE_VALIDATOR_MAP = {
    'GerritMessageValidator': GerritMessageValidator,
    'GitHubMessageValidator': GitHubMessageValidator,
}


class MetaValidator(type):
    """
    Create test class which checks the output for a message.

    It searches through `tests/data/` and loads all
    file pairs where there is a `.msg` and `.out` file. If both exist it'll
    create a test for this pair where the `.msg` is the commit message and the
    `.out` is the expected output.

    Filenames for tests that will pass validation must end with 'ok'.
    """

    def __new__(cls, name, bases, dct):
        def create_test_method(msg, expected, expected_exit_code,
                               message_validator_name):
            def test(self):
                saved_stdout = sys.stdout
                self.maxDiff = None
                try:
                    out = StringIO()
                    sys.stdout = out
                    exit_code = cmv.check_message(
                        msg.splitlines(),
                        MESSAGE_VALIDATOR_MAP[message_validator_name])
                    # For some unknown reason, assertEqual isn't always
                    # choosing the multiline method for the actual assertion.
                    self.assertMultiLineEqual(expected, out.getvalue())
                    self.assertEqual(expected_exit_code, exit_code)
                finally:
                    sys.stdout = saved_stdout
            return test

        base_path = os.path.join(
            os.path.dirname(__file__), 'data')
        for message_validator_name in os.listdir(base_path):
            specific_message_validator_test_path = os.path.join(
                base_path, message_validator_name)

            for fn in os.listdir(specific_message_validator_test_path):
                test, _, extension = fn.rpartition('.')
                fn = os.path.join(specific_message_validator_test_path, test)
                if extension == 'msg' and os.path.isfile(fn + '.out'):
                    exit_code = 0 if fn.endswith('ok') else 1
                    with open(fn + '.msg') as msg:
                        with open(fn + '.out') as out:
                            out_text = out.read().replace(
                                '%version%', cmv.__version__)
                            dct['test_' + test] = create_test_method(
                                msg.read(), out_text, exit_code,
                                message_validator_name)
        return super(MetaValidator, cls).__new__(cls, name, bases, dct)


class TestCommitMessageValidator(
        with_metaclass(MetaValidator, unittest.TestCase)):
    """Validate the commit messages using test files."""
    pass


if __name__ == '__main__':
    unittest.main()
