from api.permissions import IsAdminOwnerOrReadOnly
from api.serializers import (
    IngredientSerializer,
    TagSerializer,
    UserSerializer,
    RecipeSerializer,
)
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset для работы с моделью Tag.
    Разрешены действия только для получения списка элементов list()
    и отдельного элемента retrieve() для получения одного модели Tag.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset для работы с моделью Ingredient.
    Разрешены действия только для получения списка элементов list()
    и отдельного элемента retrieve() для получения одного модели Ingredient.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class UserViewSet(UserViewSet):
    """Viewset для работы с моделью User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOwnerOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset для работы с моделью Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminOwnerOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)

