from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    USER = ('user', 'Пользователь')
    ADMIN = ('admin', 'Администратор')


class User(AbstractUser):
    """Модель пользователя"""

    role = models.CharField(
        'роль пользователя',
        choices=UserRole.choices,
        default=UserRole.USER,
        max_length=20,
    )
    email = models.EmailField(
        'электронная почта',
        max_length=254,
        unique=True,
        blank=False,
    )
    first_name = models.CharField(
        'имя',
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        'фамилия',
        max_length=150,
        blank=False,
        null=False,
    )

    def __str__(self: any) -> str:
        return self.username

    class Meta:
        ordering = ['id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    @property
    def is_admin(self: any) -> bool:
        return self.is_superuser or self.role == UserRole.ADMIN
