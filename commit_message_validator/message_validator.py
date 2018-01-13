"""A module that contains `MessageValidator` class."""


class MessageValidator(object):
    """
    MessageValidator is an iterable class that will yields a tuple
    that contains line number and a string that describes the
    error.

    A class that implements this class, may implement:

    - `check_line()`, that yields the error message of the checked line.
    - `check_global()` (optional) that yields the error message of the
    checked lines, will be called after `check_line()` done the checking.

    See `GerritMessageValidator` for an implementation of
    `check_line()`, and `check_global()` methods.

    Example usage:

    >>> lines = ['Title', 'This should be empty', 'Body']
    >>>
    >>> class AMessageValidator(MessageValidator):
    ...     def check_line(self, lineno):
    ...         line = self._lines[lineno]
    ...         if lineno == 1 and line:
    ...             yield 'Line should be empty'
    ...     def check_global(self):
    ...         yield 'Message commit is {0} lines long'.format(
    ...             len(self._lines))
    ...
    >>> for lineno, msg in AMessageValidator(lines):
    ...     print('{0} {1}'.format(lineno, msg))
    ...
    2 Line should be empty
    3 Message commit is 3 lines long

    """

    def __init__(self, lines):
        """
        Constructor for MessageValidator.

        :param lines: list of lines from a commit message that will be checked.
        """
        self._lines = lines
        self._generator = self._check_generator()

    def check_line(self, lineno):
        """
        A function that will be called to check the commit message.

        This function should yields a string that contain description
        of what error that occured on `lineno`.

        :param lineno:       int, line number that's being checked right now.
        """
        raise NotImplementedError(
            '`check_line()` should be implemented in {0}'.format(
                type(self).__name__))

    def check_global(self):
        """
        All checks that are done after the line checks.

        This function should yields a string that contain description
        of what error that is occured.
        """
        raise NotImplementedError(
            '`check_global()` isn\'t implemented in {0}'.format(
                type(self).__name__))

    def _check_generator(self):
        """
        A generator returning each error and line number.
        """
        for lineno in range(len(self._lines)):
            for e in self.check_line(lineno):
                yield lineno + 1, e

        try:
            for e in self.check_global():
                yield len(self._lines), e
        except NotImplementedError:
            pass

    def __iter__(self):
        return self

    def __next__(self):
        """
        Return the next error of the generator.
        """
        return next(self._generator)

    def next(self):
        # For Python 2 support
        return self.__next__()
