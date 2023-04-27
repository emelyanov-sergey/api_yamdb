import re

from django.core.exceptions import ValidationError
from datetime import datetime


def validate_username(value):
    """Проверка поля username на соответствие требованиям."""
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.'),
            params={'value': value},
        )
    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', value) is None:
        raise ValidationError(
            (f'Не допустимые символы <{value}> в нике.'),
            params={'value': value},
        )


def validate_year(value):
    """Проверяем, не введён ли ещё не наступивший год."""
    if value > datetime.now().year:
        raise ValidationError(
            'Введенный год не может быть больше текущего!'
        )
