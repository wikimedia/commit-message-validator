#!/usr/bin/env python

import io
import os
import re
import sys

import pytest

import commit_message_validator as cmv
from commit_message_validator.validators.GerritMessageValidator import (
    GerritMessageValidator,
)
from commit_message_validator.validators.GitHubMessageValidator import (
    GitHubMessageValidator,
)

MESSAGE_VALIDATOR_MAP = {
    "GerritMessageValidator": GerritMessageValidator,
    "GitHubMessageValidator": GitHubMessageValidator,
}
# Regular expression for matching ANSI escape sequences
# https://stackoverflow.com/a/14693789/8171
RE_ESC = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def generate_tests():
    """
    Create test class which checks the output for a message.

    It searches through `tests/data/` and loads all
    file pairs where there is a `.msg` and `.out` file. If both exist it'll
    create a test for this pair where the `.msg` is the commit message and the
    `.out` is the expected output.

    Filenames for tests that will pass validation must end with 'ok'.
    """
    base_path = os.path.join(
        os.path.dirname(__file__),
        "data",
    )
    for message_validator_name in os.listdir(base_path):
        specific_message_validator_test_path = os.path.join(
            base_path,
            message_validator_name,
        )

        for fn in os.listdir(specific_message_validator_test_path):
            test, _, extension = fn.rpartition(".")
            fn = os.path.join(specific_message_validator_test_path, test)
            if extension == "msg" and os.path.isfile(fn + ".out"):
                exit_code = 0 if fn.endswith("ok") else 1
                with open(fn + ".msg") as msg:
                    with open(fn + ".out") as out:
                        out_text = out.read().replace(
                            "%version%",
                            cmv.__version__,
                        )
                        out_text = out_text.replace(
                            "%known_gerrit_footers%",
                            cmv.validators.GerritMessageValidator.FOOTERS_STRING,
                        )
                        yield (
                            msg.read(),
                            out_text,
                            exit_code,
                            message_validator_name,
                        )


@pytest.mark.parametrize(
    ("msg", "expected", "expected_exit_code", "message_validator_name"),
    generate_tests(),
)
def test_validator(
    msg,
    expected,
    expected_exit_code,
    message_validator_name,
):
    saved_stdout = sys.stdout
    try:
        out = io.StringIO()
        sys.stdout = out
        exit_code = cmv.check_message(
            msg.splitlines(),
            MESSAGE_VALIDATOR_MAP[message_validator_name],
        )
        # Ignore ANSI escapes in output
        plain_out = RE_ESC.sub("", out.getvalue())
        assert expected == plain_out
        assert expected_exit_code == exit_code
    finally:
        sys.stdout = saved_stdout
