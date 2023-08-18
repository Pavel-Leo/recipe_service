from typing import Any, Optional

from api.permissions import IsAdminOwnerOrReadOnly
from api.serializers import (
    UserSerializer,
    UserSubscriptionSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
)
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from users.models import User, Subscription


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
    и для получения отдельного элемента - retrieve() модели Ingredient.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class UserViewSet(DjoserUserViewSet):
    """Viewset для работы с моделью User."""

    queryset = User.objects.all()
    permission_classes = (IsAdminOwnerOrReadOnly,)
    serializer_class = UserSerializer

    @action(
        methods=('get',), detail=False, permission_classes=(IsAuthenticated,), url_path='subscribtions',
    )
    def subscribtions(self, request: Request) -> Response:
        user = self.request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = UserSubscriptionSerializer(pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='subscribe')
    def subscribe(self, request: Request, pk: Optional[int] = None) -> Response:
        user = self.request.user
        author = get_object_or_404(User, id=pk)
        is_follow: bool = Subscription.objects.filter(
            user=user,
            author=author,
        ).exists()

        if request.method == 'POST':
            if user == author:
                message = {'errors': ['Нельзя подписаться на себя!']}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            if is_follow:
                message = {'errors': ['Подписка на автора уже существует!']}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(user=user, author=author)
            serializer = UserSubscriptionSerializer(
                author, context={'request': request},
            )
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if is_follow:
                Subscription.objects.get(user=user, author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            message = {'errors': ['Подписка на автора не существует!']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset для работы с моделью Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminOwnerOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)

