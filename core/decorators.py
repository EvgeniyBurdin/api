""" Модуль для декораторов обработчиков.
"""
from valdec.decorators import async_validate
from valdec.data_classes import Settings
from valdec.validator_pydantic import validator


# Декоратор, который будет валидировать данные, и конвертировать их в
# класс (классы) DC, если они присутствуют в аннотации аргумента и/или
# возврата валидируемой функции (или метода):
validate = async_validate

# ----------------------------------------------------------------------------

custom_settings = Settings(
    validator=validator,
    is_replace_args=False,    # Не конвертируем аргументы
    is_replace_result=False,  # Не конвертируем результат
)


# Декоратор, который будет только валидировать аргументы и/или возврат функции
# или метода (сами данные останутся в том виде, в каком они были):
def validate_raw(*args, **kwargs):  # define new decorator
    kwargs["settings"] = custom_settings
    return async_validate(*args, **kwargs)
