from typing import Tuple
from django.contrib import admin

from .models import Ingredient, Recipe, Tag, RecipeIngredient, Subscription


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display: Tuple[str] = ('name', 'slug', 'color')
    search_fields: Tuple[str] = ('name',)
    list_editable: Tuple[str] = ('color', 'slug', 'name')
    prepopulated_fields: Tuple[str] = {'slug': ('name',)}


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display: Tuple[str] = ('name', 'author', 'favorite_count')
    search_fields: Tuple[str] = ('name', 'author__username', 'tags__name')
    list_editable: Tuple[str] = ('tags',)
    readonly_fields: Tuple[str] = ('favorite_count',)
