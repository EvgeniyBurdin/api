from valdec.decorators import async_validate
from valdec.data_classes import Settings
from valdec.validator_pydantic import validator


custom_settings = Settings(
    validator=validator,
    is_replace_args=False,
    is_replace_result=False,
)


def only_validate(*args, **kwargs):  # define new decorator
    kwargs["settings"] = custom_settings
    return async_validate(*args, **kwargs)
