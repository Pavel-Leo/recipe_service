from typing import Tuple

from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display: Tuple[str] = ('id', 'name', 'slug', 'color')
    search_fields: Tuple[str] = ('name',)
    list_editable: Tuple[str] = ('color', 'slug', 'name')
    prepopulated_fields: Tuple[str] = {'slug': ('name',)}
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display: Tuple[str] = ('id', 'name', 'author', 'favorite_count')
    search_fields: Tuple[str] = ('name', 'author__username', 'tags__name')
    list_editable: Tuple[str] = ('tags',)
    readonly_fields: Tuple[str] = ('favorite_count',)
    inlines: Tuple[RecipeIngredientInline] = (RecipeIngredientInline,)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display: Tuple[str] = ('id', 'name', 'measurement_unit')
    list_filter: Tuple[str] = ('name',)
    search_fields: Tuple[str] = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display: Tuple[str] = ('id', 'user', 'recipe')
    list_filter: Tuple[str] = ('user', 'recipe')
    search_fields: Tuple[str] = ('user__username', 'recipe__name')
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display: Tuple[str] = ('id', 'user', 'recipe')
    list_filter: Tuple[str] = ('user', 'recipe')
    search_fields: Tuple[str] = ('user__username', 'recipe__name')
    empty_value_display = '-пусто-'