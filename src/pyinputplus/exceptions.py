class PyInputPlusError(Exception):
    """Base class for exceptions raised when PyInputPlus functions encounter a problem.

    If PyInputPlus raises an exception that isn't this class, that indicates a bug in
    the module.
    """


class ValidationError(PyInputPlusError):
    """Exception for when user input fails validation.

    This exception is raised when a `validate*()` function is called and the input
    fails validation. For example, `validateInt('four')` will raise this. This
    exception class is for all the PySimpleValidate wrapper functions
    (`validateStr()`, etc.) that PyInputPlus provides so that
    `pyinputplus.exceptions.ValidationError` is raised instead of
    `pysimplevalidate.ValidationError`.
    """


class PyIPTimeoutError(PyInputPlusError):
    """The user has failed to enter valid input before the timeout."""


class RetryLimitError(PyInputPlusError):
    """The user has failed to enter valid input within a number of tries."""
