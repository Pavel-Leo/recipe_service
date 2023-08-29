from typing import Tuple

from django.contrib import admin

from recipes.models import (
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
    list_filter: Tuple[str] = ('name',)
    prepopulated_fields: Tuple[str] = {'slug': ('name',)}
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display: Tuple[str] = (
        'id',
        'name',
        'author',
        'added_to_favorites',
    )
    readonly_fields = ('added_to_favorites',)
    list_filter: Tuple[str] = ('name', 'author', 'tags')
    search_fields: Tuple[str] = ('name', 'author__username', 'tags__name')
    inlines: Tuple[RecipeIngredientInline] = (RecipeIngredientInline,)
    empty_value_display = '-пусто-'

    def added_to_favorites(self, obj: Recipe) -> int:
        return obj.favorites.count()

    added_to_favorites.short_description = 'Добавлено в избранное'


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
class ShoppingCart(admin.ModelAdmin):
    list_display: Tuple[str] = ('id', 'user', 'recipe')
    list_filter: Tuple[str] = ('user', 'recipe')
    search_fields: Tuple[str] = ('user__username', 'recipe__name')
    empty_value_display = '-пусто-'
