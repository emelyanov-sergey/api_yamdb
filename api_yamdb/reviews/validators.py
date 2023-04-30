from django.core.exceptions import ValidationError
from datetime import datetime


def validate_year(value):
    """Проверяем, не введён ли ещё не наступивший год."""
    if value > datetime.now().year:
        raise ValidationError(
            'Введенный год не может быть больше текущего!'
        )
