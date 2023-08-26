from typing import Dict, List

from api.filters import RecipeFilter
from api.paginations import CustomPagination
from api.permissions import IsAdminOwnerOrReadOnly
from api.serializers import (
    IngredientSerializer,
    RecipeCartFavoriteSerializer,
    RecipeGetSerializer,
    RecipePostOrPatchSerializer,
    TagSerializer,
    UserSerializer,
    UserSubscriptionSerializer,
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
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
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from users.models import Subscription

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset для работы с моделью Tag.
    Разрешены действия только для получения списка элементов list()
    и отдельного элемента retrieve() для получения одного модели Tag.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset для работы с моделью Ingredient.
    Разрешены действия только для получения списка элементов list()
    и для получения отдельного элемента - retrieve() модели Ingredient.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class UserViewSet(DjoserUserViewSet):
    """Viewset для работы с моделью User."""

    pagination_class = CustomPagination
    serializer_class = UserSerializer

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request: Request) -> Response:
        """Определяет URL-путь для вызова действия возврата подписок
        текущего пользователя.
        Запрос к эндпоинту /subscriptions/.
        Поддерживает только GET запросы на получение списка подписок.
        """
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
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request: Request, id: int) -> Response:
        """Определяет URL-путь для вызова действия создания подписки
        текущего пользователя на автора рецепта.
        Запрос к эндпоинту /subscribe/.
        Поддерживает только POST-запросы добавления автора рецепта в подписки
        текущего пользователя и DELETE запросы на удаление автора рецепта из
        подписок текущего пользователи.
        """
        user = self.request.user
        author = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            if (
                user != author
                and not Subscription.objects.filter(
                    user=user,
                    author=author,
                ).exists()
            ):
                Subscription.objects.create(
                    user=user,
                    author=author,
                )
                serializer = UserSubscriptionSerializer(
                    author,
                    context={'request': request},
                )
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED,
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if Subscription.objects.filter(
                user=user,
                author=author,
            ).exists():
                follow = get_object_or_404(
                    Subscription,
                    user=user,
                    author=author,
                )
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset для работы с моделью Recipe."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOwnerOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = RecipeFilter
    ordering = ('-id',)

    def perform_create(self, serializer: Serializer) -> None:
        serializer.save(author=self.request.user)

    def get_serializer_class(self) -> Serializer:
        if self.action == 'create' or self.action == 'partial_update':
            return RecipePostOrPatchSerializer
        return RecipeGetSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,),
        serializer_class=RecipeCartFavoriteSerializer,
    )
    def shopping_cart(
        self,
        request: Request,
        pk: int = None,
    ) -> Response:
        """
        Определяет URL-путь для вызова действия добавления рецепта в корзину.
        Запрос к эндпоинту /shopping_cart/.
        Поддерживает только POST-запросы добавления рецепта в корзину и
        DELETE запросы на удаление рецепта из корзины покупок.
        """
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if not ShoppingCart.objects.filter(
                user=user, recipe=recipe,
            ).exists():
                ShoppingCart.objects.create(user=user, recipe=recipe)
                serializer = RecipeCartFavoriteSerializer(
                    recipe,
                    context={'request': request},
                )
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED,
                )
            message: Dict[str, str] = {
                'error': 'Рецепт уже добавлен в список покупок.',
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            if not ShoppingCart.objects.filter(
                user=user, recipe=recipe,
            ).exists():
                message: Dict[str, str] = {
                    'error': 'Рецепта нет в списке покупок.',
                }
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            shoppig_cart = get_object_or_404(
                ShoppingCart, user=user, recipe=recipe,
            )
            shoppig_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete'),
        detail=True,
        serializer_class=RecipeCartFavoriteSerializer(),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(
        self,
        request: Request,
        pk: int = None,
    ) -> Response:
        """
        Определяет URL-путь для вызова действия добавления рецепта в избранное.
        Запрос к эндпоинту /favorite/.
        Поддерживает только POST-запросы добавления рецепта в избранное и
        DELETE запросы на удаление рецепта из избранного.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                Favorite.objects.create(user=user, recipe=recipe)
                serializer = RecipeCartFavoriteSerializer(
                    recipe,
                    context={'request': request},
                )
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED,
                )
            message: Dict[str, str] = {
                'error': 'Рецепт уже добавлен в избранное.',
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                message: Dict[str, str] = {'error': 'Рецепта нет в избранном.'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request: Request) -> FileResponse:
        """Определяет URL-путь для вызова действия получения списка покупок.
        Запрос к эндпоинту /download_shopping_cart/.
        Поддерживает только GET запросы на получение списка покупок.
        """
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__carts__user=request.user,
            )
            .order_by('ingredient__name')
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(ingredient_value=Sum('amount'))
        )
        preview = (
            'Полный список ингредиентов для рептов из списка покупок'
            f' {request.user.get_full_name()}:\n'
        )
        list_for_shopping: List[str] = []
        for ingredient in ingredients:
            list_for_shopping.append(
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['ingredient_value']}",
            )
        list_for_shopping.sort(key=lambda x: x.lower())
        list_for_shopping.insert(0, preview)
        shopping_list = ''.join(list_for_shopping)
        path_to_file = (
            f'{settings.MEDIA_ROOT}\\buy_list\\'
            f'{request.user.username}_shopping_list.txt'
        )
        with open(path_to_file, 'w+') as file:
            file.write(shopping_list)
        return FileResponse(
            open(path_to_file, 'rb'),
            status=status.HTTP_200_OK,
        )
