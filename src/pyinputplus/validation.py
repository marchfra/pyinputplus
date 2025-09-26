"""Wrap all of the PySimpleValidate functions.

This is done so that they can be called from PyInputPlus and will raise
`pyinputplus.exceptions.ValidationError` instead of `pysimplevalidate.ValidationError`.
"""

for function_name in (
    "validateStr",
    "validateNum",
    "validateInt",
    "validateFloat",
    "validateChoice",
    "validateTime",
    "validateDate",
    "validateDatetime",
    "validateFilename",
    "validateFilepath",
    "validateIP",
    "validateIPv4",
    "validateIPv6",
    "validateRegex",
    "validateRegexStr",
    "validateURL",
    "validateEmail",
    "validateYesNo",
    "validateBool",
    "validateUSState",
    "validateName",
    "validateAddress",
    "validatePhone",
    "validateMonth",
    "validateDayOfWeek",
    "validateDayOfMonth",
):
    exec(f"""def {function_name}(value, *args, **kwargs):
    try:
        return pysv.{function_name}(value, *args, **kwargs)
    except pysv.ValidationError as e:
        raise ValidationError(str(e))""")
