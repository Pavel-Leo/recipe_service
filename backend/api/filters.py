from typing import List

from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (BooleanFilter,
                                                   ModelMultipleChoiceFilter)
from recipes.models import Recipe, Tag

User = get_user_model()


class RecipeFilter(FilterSet):
    """Кастомный класс фильтрации.
    Позволяет выполнять фильтрацию рецептов по различным параметрам, включая
    наличие рецептов в списке избранного и списке покупок пользователя.
    """

    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model: Recipe = Recipe
        fields: List[str] = ['tags', 'author']

    def filter_is_favorited(
        self, queryset: QuerySet, name: str, value: bool,
    ) -> QuerySet:
        """Производит фильтрацию queryset рецептов по наличию их в избранном
        пользователя. Возвращает отфильтрованный queryset рецептов.
        """
        user: User = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(
        self, queryset: QuerySet, name: str, value: bool,
    ) -> QuerySet:
        """Производит фильтрацию queryset рецептов по наличию их в списке
        покупок пользователя. Возвращает отфильтрованный queryset рецептов.
        """
        user: User = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(carts__user=user)
        return queryset
