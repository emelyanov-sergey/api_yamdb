import re
from datetime import datetime

from django.core.exceptions import ValidationError


def validate_year(value):
    """Проверяем, не введён ли ещё не наступивший год."""
    if value > datetime.now().year:
        raise ValidationError(
            'Введенный год не может быть больше текущего!'
        )


def validate_username(value):
    """В качестве ника запрещает использовать 'me'."""
    if value == 'me':
        raise ValidationError(
            'Запрещенное имя пользователя - "me".'
        )
    forbidden_symbols = ''.join(set(re.sub(r'^[\w.@+-]+$', '', value)))
    if forbidden_symbols:
        raise ValidationError(
            f'Некорректный символ для никнейма: {forbidden_symbols}'
            f' Только буквы, цифры и @/./+/-/_'
        )
    return value
