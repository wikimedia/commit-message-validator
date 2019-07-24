import pytest


from commit_message_validator.message_validator import MessageValidator


class NoCheckLineMessageValidator(MessageValidator):
    """
    A MessageValidator that doesn't implement `check_line()` and
    `check_global()`.
    """


class JustTestMessageValidator(MessageValidator):

    def check_line(self, lineno):
        if lineno == 1:
            yield 'Error on line 2'
        elif lineno == 3:
            yield 'Error on line 4'

    def check_global(self):
        yield 'From global check'


class NoCheckGlobalMessageValidator(MessageValidator):

    def check_line(self, lineno):
        if lineno == 1:
            yield 'Error on line 2'
        elif lineno == 3:
            yield 'Error on line 4'


class TestMessageValidator:

    def test_check_line_not_implemented(self):
        # If 'check_line()` is not implemented, the method should raise
        # NotImplementedError.
        lines = ['This is a line']
        no_check_line_mv = NoCheckLineMessageValidator(lines)
        with pytest.raises(NotImplementedError) as e:
            no_check_line_mv.check_line(0)
        assert str(e.value) == '`check_line()` should be implemented in NoCheckLineMessageValidator'

    def test_check_global_not_implemented_but_called(self):
        # If 'check_global()` is not implemented, but called,
        # the method should raise NotImplementedError.
        lines = ['This is a line']
        no_check_line_mv = NoCheckLineMessageValidator(lines)

        with pytest.raises(NotImplementedError) as e:
            no_check_line_mv.check_global()
        assert str(e.value) == '`check_global()` isn\'t implemented in NoCheckLineMessageValidator'

    def test_iterate_iterable_message_validator(self):
        lines = ['This is a line', '2nd line', '3rd line', '4th line', '5th']

        expected_result = [(lineno, msg)
                           for lineno, msg in
                           JustTestMessageValidator(lines)]
        assert expected_result == [
            (2, 'Error on line 2'),
            (4, 'Error on line 4'),
            (5, 'From global check'),
        ]

    def test_iterate_iterable_message_validator_no_check_global(self):
        lines = ['This is a line', '2nd line', '3rd line', '4th line', '5th']

        expected_result = [(lineno, msg)
                           for lineno, msg in
                           NoCheckGlobalMessageValidator(lines)]
        assert expected_result == [
            (2, 'Error on line 2'),
            (4, 'Error on line 4'),
        ]

    def test_iterate_with_next_method(self):
        lines = ['This is a line', '2nd line', '3rd line', '4th line', '5th']

        just_test_mv = JustTestMessageValidator(lines)
        assert (2, 'Error on line 2') == just_test_mv.next()
