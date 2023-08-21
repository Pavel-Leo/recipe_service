from typing import Optional

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription, User

from api.permissions import IsAdminOrReadOnly, IsAdminOwnerOrReadOnly
from api.serializers import (IngredientSerializer, RecipeGetSerializer,
                             RecipePostOrPatchSerializer,
                             RecipeShopCartSerializer, TagSerializer,
                             UserSerializer, UserSubscriptionSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset для работы с моделью Tag.
    Разрешены действия только для получения списка элементов list()
    и отдельного элемента retrieve() для получения одного модели Tag.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset для работы с моделью Ingredient.
    Разрешены действия только для получения списка элементов list()
    и для получения отдельного элемента - retrieve() модели Ingredient.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class UserViewSet(DjoserUserViewSet):
    """Viewset для работы с моделью User."""

    queryset = User.objects.all()
    permission_classes = (IsAdminOwnerOrReadOnly,)
    serializer_class = UserSerializer

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='subscribtions',
    )
    def subscribtions(self, request: Request) -> Response:
        user = self.request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = UserSubscriptionSerializer(
            pages,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='subscribe',
    )
    def subscribe(
        self,
        request: Request,
        pk: Optional[int] = None,
    ) -> Response:
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
                author,
                data=request.data,
                context={'request': request},
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
            )

        elif request.method == 'DELETE':
            if is_follow:
                subscription = get_object_or_404(
                    Subscription,
                    user=user,
                    author=author,
                )
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            message = {'errors': ['Вы не подписаны на автора!']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset для работы с моделью Recipe."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOwnerOrReadOnly, IsAdminOrReadOnly)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(author=self.request.user)

    def get_serializer_class(self) -> Serializer:
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeGetSerializer
        return RecipePostOrPatchSerializer

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path=r'shopping_cart',
    )
    def shopping_cart(
        self,
        request: Request,
        pk: Optional[int] = None,
    ) -> Response:
        """
        Запрос к эндпоинту /shopping_cart/.
        Поддерживает только POST-запросы добавления рецепта в корзину и
        DELETE запросы на удаление рецепта из корзины покупок.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                message = {'error': 'Рецепт уже добавлен в корзину.'}
                return Response(
                    data=message,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeShopCartSerializer(
                recipe,
                context={'request': request},
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
            )

        elif request.method == 'DELETE':
            shopping_cart = get_object_or_404(
                ShoppingCart,
                user=user,
                recipe=recipe,
            )
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path=r'favorite',
    )
    def favorite(
        self,
        request: Request,
        pk: Optional[int] = None,
    ) -> Response:
        """
        Запрос к эндпоинту /favorite/.
        Поддерживает только POST-запросы добавления рецепта в избранное и
        DELETE запросы на удаление рецепта из избранного.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                message = {'error': 'Рецепт уже добавлен в избранное.'}
                return Response(
                    data=message,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeShopCartSerializer(
                recipe,
                context={'request': request},
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED,
            )

        elif request.method == 'DELETE':
            favorite_list = get_object_or_404(
                Favorite,
                user=user,
                recipe=recipe,
            )
            favorite_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request: Request) -> Response:
        user = self.request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=user,
        ).values('ingredient__name', 'ingredient__measurement_unit', 'amount')
        ingredients_data = {}
        for ingr in ingredients:
            name_unit = (
                f'{ingr["ingredient__name"]}'
                f'({ingr["ingredient__measurement_unit"]})'
            )
            amount = ingr['amount']
            if name_unit in ingredients_data:
                ingredients_data[name_unit] += amount
            else:
                ingredients_data[name_unit] = amount
        ingredients_list = 'Список покупок:\n'
        for key, value in ingredients_data.items():
            ingredients_list += f'{key}: {value}\n'
        file = 'shopping_cart.txt'
        response = HttpResponse(ingredients_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response
