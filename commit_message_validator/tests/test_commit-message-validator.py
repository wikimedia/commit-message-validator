#!/usr/bin/env python

import os
import sys
import unittest

import commit_message_validator as cmv

if sys.version_info[0] > 2:
    from io import StringIO
else:
    from StringIO import StringIO


class MetaValidator(type):

    """
    Create test class which checks the output for a message.

    It searches through `tests/data/` and loads all
    file pairs where there is a `.msg` and `.out` file. If both exist it'll
    create a test for this pair where the `.msg` is the commit message and the
    `.out` is the expected output.
    """

    def __new__(cls, name, bases, dct):
        def create_test_method(msg, expected, expected_exit_code):
            def test(self):
                saved_stdout = sys.stdout
                try:
                    out = StringIO()
                    sys.stdout = out
                    exit_code = cmv.check_message(msg.splitlines())
                    self.assertEqual(expected, out.getvalue())
                    self.assertEqual(exit_code, expected_exit_code)
                finally:
                    sys.stdout = saved_stdout
            return test

        base_path = os.path.join(os.path.dirname(__file__),
                                 'data')
        for fn in os.listdir(base_path):
            test, _, extension = fn.rpartition('.')
            fn = os.path.join(base_path, test)
            if extension == 'msg' and os.path.isfile(fn + '.out'):
                exit_code = 0 if fn.endswith('ok') else 1
                with open(fn + '.msg') as msg:
                    with open(fn + '.out') as out:
                        out_text = out.read().replace('%version%', cmv.__version__)
                        dct['test_' + test] = create_test_method(
                            msg.read(), out_text, exit_code)
        return super(MetaValidator, cls).__new__(cls, name, bases, dct)


class TestCommitMessageValidator(unittest.TestCase):

    """Validate the commit messages using test files."""

    __metaclass__ = MetaValidator


if __name__ == '__main__':
    unittest.main()
