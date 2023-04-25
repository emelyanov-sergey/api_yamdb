"""Создал валидаторы на всякий случай. Пускай лучше будут. Если что, их можно дополнить."""
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """Проверяем, не введён ли ещё не наступивший год."""

    if value > timezone.now().year:
        raise ValidationError(
            ('Год %(value)s больше текущего!'),
            params={'value': value},
        )