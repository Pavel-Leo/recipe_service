from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    """Кастомная переопределенная модель пользователя."""

    USERNAME_FIELD = 'email'

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
    username = models.CharField(max_length=150, unique=True)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def __str__(self: any) -> str:
        return self.username

    class Meta:
        ordering = ['id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'


class Subscription(models.Model):
    """Модель подписок на автора рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор',
    )

    def clean(self) -> None:
        if self.user == self.author:
            raise ValidationError('Подписка на себя недопустима')

    class Meta:
        ordering = ['-id']
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_subscription',
            ),
        ]

    def __str__(self: any) -> str:
        return f'{self.user} подписан на {self.author}'
