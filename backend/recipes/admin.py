from django.contrib import admin

from .models import Ingredient, Recipe, Tag, RecipeIngredient, Subscription


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    search_fields = ('name',)
    list_editable = ('color', 'slug', 'name')
    prepopulated_fields = {'slug': ('name',)}
