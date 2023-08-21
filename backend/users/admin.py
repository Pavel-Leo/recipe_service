from typing import Tuple

from django.contrib import admin
from users.models import Subscription, User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display: Tuple[str] = (
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
    )
    search_fields: Tuple[str] = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter: Tuple[str] = (
        'username',
        'email',
    )
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display: Tuple[str] = ('user', 'author')
    list_filter: Tuple[str] = ('user', 'author')
    search_fields: Tuple[str] = ('user__username', 'author__username')
    empty_value_display: str = '-пусто-'
