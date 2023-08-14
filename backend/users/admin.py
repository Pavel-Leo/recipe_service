from typing import Tuple
from django.contrib import admin

from users.models import User, Subscription


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display: Tuple[str] = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'password',
    )
    search_fields: Tuple[str] = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
    )
    list_filter: Tuple[str] = (
        'username',
        'email',
    )
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display: Tuple[str] = (
        'user',
        'author',
    )
    search_fields: Tuple[str] = (
        'user',
        'author',
    )
    list_filter: Tuple[str] = (
        'user',
        'author',
    )
    empty_value_display = '-пусто-'