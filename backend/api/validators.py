from rest_framework.exceptions import ValidationError


def check_username(value: str) -> str:
    """Проверка имени пользователя на валидность данных."""
    if value.lower() == 'me':
        raise ValidationError('Нельзя использовать имя "me" или "ME"')
    return value
