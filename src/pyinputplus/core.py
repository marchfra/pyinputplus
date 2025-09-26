import logging
import time
from collections.abc import Callable

import pwinput

from .exceptions import PyInputPlusError, PyIPTimeoutError, RetryLimitError

logger = logging.getLogger(__name__)


def parameters():
    """Common parameters for all ``input*()`` functions in PyInputPlus:

    * ``prompt`` (str): The text to display before each prompt for user input. Identical to the prompt argument for Python's ``raw_input()`` and ``input()`` functions.
    * ``default`` (str, None): A default value to use should the user time out or exceed the number of tries to enter valid input.
    * ``blank`` (bool): If ``True``, a blank string will be accepted. Defaults to ``False``.
    * ``timeout`` (int, float): The number of seconds since the first prompt for input after which a ``PyIPTimeoutError`` is raised the next time the user enters input.
    * ``limit`` (int): The number of tries the user has to enter valid input before the default value is returned.
    * ``strip`` (bool, str, None): If ``None``, whitespace is stripped from value. If a str, the characters in it are stripped from value. If ``False``, nothing is stripped.
    * ``allowlistRegexes`` (Sequence, None): A sequence of regex str that will explicitly pass validation.
    * ``blocklistRegexes`` (Sequence, None): A sequence of regex str or ``(regex_str, error_msg_str)`` tuples that, if matched, will explicitly fail validation.
    * ``applyFunc`` (Callable, None): An optional function that is passed the user's input, and returns the new value to use as the input.
    * ``postValidateApplyFunc`` (Callable, None): An optional function that is passed the user's input after it has passed validation, and returns a transformed version for the ``input*()`` function to return.
    """
    # This "function" only exists so you can call `help()`


def _check_limit_and_timeout(
    start_time: float,
    timeout: float | None,
    tries: int,
    limit: int | None,
) -> None | PyIPTimeoutError | RetryLimitError:
    """Returns a ``PyIPTimeoutError`` or ``RetryLimitError`` if the user has
    exceeded those limits, otherwise returns ``None``.

    * ``startTime`` (float): The Unix epoch time when the input function was first called.
    * ``timeout`` (float): A number of seconds the user has to enter valid input.
    * ``tries`` (int): The number of times the user has already tried to enter valid input.
    * ``limit`` (int): The number of tries the user has to enter valid input.
    """
    # NOTE: We return exceptions instead of raising them so the caller
    # can still display the original validation exception message.
    if timeout is not None and start_time + timeout < time.time():
        return PyIPTimeoutError()

    if limit is not None and tries >= limit:
        return RetryLimitError()

    return None  # Returns None if there was neither a timeout or limit exceeded.


def _generic_input[T](
    prompt: str = "",
    default_value: T | None = None,
    timeout: float | None = None,
    limit: int | None = None,
    apply_func: Callable[[str], T] | None = None,
    validation_func: Callable[[str | T], T] | None = None,
    post_validate_apply_func: Callable[[str, T], T] | None = None,
    password_mask: str | None = None,
) -> T:  # TODO: finish docstring
    """Core function to get user input and validate it.

    This function is used by the various input_*() functions to handle the common
    operations of each input function: displaying prompts, collecting input, handling
    timeouts, etc.

    See the `input_*()` functions for examples of usage.

    Note that the user must provide valid input within both the timeout limit
    AND the retry limit, otherwise ``PyIPTimeoutError`` or ``RetryLimitError`` is
    raised (unless there's a default value provided, in which case the default
    value is returned.)

    Note that the ``postValidateApplyFunc()`` is not called on the default value,
    if a default value is provided.

    Run `help(pyinputplus.parameters)` for an explanation of the common parameters.

    # * ``passwordMask`` (str, None): An optional argument. If not ``None``, this ``getpass.getpass()`` is used instead of
    """
    # NOTE: _generic_input() can return any type of value. Any type casting must be done
    # by the caller.

    # Validate the parameters.
    if not isinstance(prompt, str):
        raise PyInputPlusError("prompt argument must be a str")
    if not isinstance(timeout, (int, float, type(None))):
        raise PyInputPlusError("timeout argument must be an int or float")
    if not isinstance(limit, (int, type(None))):
        raise PyInputPlusError("limit argument must be an int")
    if not callable(validation_func):
        raise PyInputPlusError("validationFunc argument must be a function")
    if not (callable(apply_func) or apply_func is None):
        raise PyInputPlusError("applyFunc argument must be a function or None")
    if not (callable(post_validate_apply_func) or post_validate_apply_func is None):
        raise PyInputPlusError(
            "postValidateApplyFunc argument must be a function or None",
        )
    if password_mask is not None and (
        not isinstance(password_mask, str) or len(password_mask) > 1
    ):
        raise PyInputPlusError(
            "passwordMask argument must be None or a single-character string.",
        )

    start_time = time.time()
    tries = 0

    while True:
        # Get the user input.
        print(prompt, end="")
        if password_mask is None:
            user_input = input()
        else:
            user_input = str(pwinput.pwinput(prompt="", mask=password_mask))
        tries += 1

        # Transform the user input with the apply_func function.
        if apply_func is not None:
            user_input = apply_func(user_input)

        # Run the validation function.
        try:
            possible_new_user_input = validation_func(
                user_input,
            )  # If validation fails, this function will raise an exception. Returns an updated value to use as user input (e.g. stripped of whitespace, etc.)
            if possible_new_user_input is not None:
                user_input = possible_new_user_input
        except Exception as exc:
            # Check if they have timed out or reach the retry limit. (If so,
            # the PyIPTimeoutError/RetryLimitError overrides the validation
            # exception that was just raised.)
            limit_or_timeout_error = _check_limit_and_timeout(
                start_time=start_time,
                timeout=timeout,
                tries=tries,
                limit=limit,
            )

            print(exc)  # Display the message of the validation exception.
            logger.exception("UH_OH", exc_info=exc)  # TODO: write a decent log

            if isinstance(limit_or_timeout_error, Exception):
                if default_value is not None:
                    # If there was a timeout/limit exceeded, return the default value if there is one.
                    return default_value
                # If there is no default, then raise the timeout/limit exception.
                raise limit_or_timeout_error
            # If there was no timeout/limit exceeded, let the user enter input again.
            continue

        # The previous call to _checkLimitAndTimeout() only happens when the
        # user enteres invalid input. Now we should check for a timeout even if
        # the last input was valid.
        if timeout is not None and start_time + timeout < time.time():
            # It doesn't matter that the user entered valid input, they've
            # exceeded the timeout so we either return the default or raise
            # PyIPTimeoutError.
            if default_value is not None:
                return default_value
            raise PyIPTimeoutError

        if post_validate_apply_func is not None:
            return post_validate_apply_func(user_input)
        return user_input
