# Copyright (c) 2023 Wikimedia Foundation and contributors.
# All Rights Reserved.
#
# This file is part of Commit Message Validator.
#
# Commit Message Validator is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Commit Message Validator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Commit Message Validator.  If not, see <http://www.gnu.org/licenses/>.
import io
import os
import re
import sys

import pytest

from commit_message_validator.lint import check_message
from commit_message_validator.validators import GerritMessageValidator
from commit_message_validator.validators import GitHubMessageValidator
from commit_message_validator.validators import GitLabMessageValidator
from commit_message_validator.validators.wikimedia import EXPECTED_FOOTERS

MESSAGE_VALIDATOR_MAP = {
    "GerritMessageValidator": GerritMessageValidator,
    "GitHubMessageValidator": GitHubMessageValidator,
    "GitLabMessageValidator": GitLabMessageValidator,
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

    Filenames for tests that will pass validation must end with 'ok' and can
    omit an explict '.out' file as 'ok.out' will be assumed.
    """
    base_path = os.path.join(
        os.path.dirname(__file__),
        "data",
    )
    footers_string = ", ".join(footer for footer in EXPECTED_FOOTERS)
    for message_validator_name in os.listdir(base_path):
        if message_validator_name not in MESSAGE_VALIDATOR_MAP:
            continue

        specific_message_validator_test_path = os.path.join(
            base_path,
            message_validator_name,
        )

        for fn in os.listdir(specific_message_validator_test_path):
            test, _, extension = fn.rpartition(".")
            fn = os.path.join(specific_message_validator_test_path, test)
            if extension == "msg":
                exit_code = 0 if fn.endswith("ok") else 1
                with open(fn + ".msg") as msg:
                    out_fn = fn + ".out"
                    if not os.path.isfile(out_fn):
                        if exit_code == 0:
                            out_fn = os.path.join(
                                specific_message_validator_test_path,
                                "ok.out",
                            )
                        else:
                            pytest.fail(
                                "No .out file found for {}.msg".format(
                                    os.path.relpath(fn, base_path),
                                ),
                            )
                    with open(out_fn) as out:
                        # FIXME: footers_string is a gross hack now
                        out_text = out.read().replace(
                            "%known_gerrit_footers%",
                            footers_string,
                        )
                        yield pytest.param(
                            msg.read(),
                            out_text,
                            exit_code,
                            message_validator_name,
                            id=os.path.relpath(fn, base_path),
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
        exit_code = check_message(
            msg.splitlines(),
            MESSAGE_VALIDATOR_MAP[message_validator_name],
        )
        # Ignore ANSI escapes in output
        plain_out = RE_ESC.sub("", out.getvalue())
        assert plain_out == expected
        assert exit_code == expected_exit_code
    finally:
        sys.stdout = saved_stdout
