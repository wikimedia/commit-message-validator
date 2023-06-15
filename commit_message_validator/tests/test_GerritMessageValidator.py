from commit_message_validator.validators.GerritMessageValidator import (
    CommitMessageContext,
)
from commit_message_validator.validators.GerritMessageValidator import (
    GerritMessageValidator,
)


def test_context_handler():
    lines = [
        "Commit header",
        "",
        "Commit body message",
        "",
        "Change-Id: I00d0f7c3b294c3ddc656f9a5447df89c63142203",
    ]

    gerrit_mv = GerritMessageValidator(lines)

    expected_result = [
        CommitMessageContext.HEADER,
        CommitMessageContext.BODY,
        CommitMessageContext.BODY,
        CommitMessageContext.BODY,
        CommitMessageContext.FOOTER,
    ]

    result = [gerrit_mv.get_context(lineno) for lineno in range(len(lines))]
    assert expected_result == result
