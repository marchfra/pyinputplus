"""PyInputPlus by Al Sweigart.

A Python 2 and 3 module to provide input()- and raw_input()-like functions with
additional validation features.
"""

import gettext
from pathlib import Path

from .core import parameters
from .exceptions import (
    PyInputPlusError,
    PyIPTimeoutError,
    RetryLimitError,
    ValidationError,
)
from .inputs import *
from .validations import *
from .version import __version__

FOLDER_OF_THIS_FILE = Path(__file__).parent
en_lang = gettext.translation(
    "pyinputplus",
    localedir=FOLDER_OF_THIS_FILE / "locale",
    languages=["en"],
)
en_lang.install()
# TODO - should i have a setLang() function?

# TODO - Figure out a way to get doctests to work with input().

# TODO - Possible future feature: using cmdline for tab-completion and history.

__all__ = [
    # Exceptions
    "PyIPTimeoutError",
    "PyInputPlusError",
    "RetryLimitError",
    "ValidationError",
    # Version
    "__version__",
    # Core functions
    "parameters",
    # Input functions
    # Validation functions
]
