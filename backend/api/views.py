from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from backend.api import serializers
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User
from api.serializers import TagSerializer, IngredientSerializer, UserSerializer
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from api.permissions import IsAdminOwnerOrReadOnly


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


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminOwnerOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)

    