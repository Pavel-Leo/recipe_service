from django.shortcuts import get_object_or_404, render
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination
from users.models import Subscription, User


