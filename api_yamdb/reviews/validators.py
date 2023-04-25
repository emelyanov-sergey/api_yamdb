import re

from django.core.exceptions import ValidationError
from django.utils import timezone


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

    if value > timezone.now().year:
        raise ValidationError(
            ('Год %(value)s больше текущего!'),
            params={'value': value},
        )
