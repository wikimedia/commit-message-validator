from commit_message_validator.validators import GerritMessageValidator


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
        GerritMessageValidator.MessageContext.HEADER,
        GerritMessageValidator.MessageContext.BODY,
        GerritMessageValidator.MessageContext.BODY,
        GerritMessageValidator.MessageContext.BODY,
        GerritMessageValidator.MessageContext.FOOTER,
    ]

    result = [gerrit_mv.get_context(lineno) for lineno in range(len(lines))]
    assert expected_result == result
