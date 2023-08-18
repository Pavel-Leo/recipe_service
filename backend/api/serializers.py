import base64
from typing import Tuple

from django.core.files.base import ContentFile

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from rest_framework import serializers
from users.models import Subscription, User


class Base64ImageField(serializers.ImageField):
    """Переопределяет поведение поля изображения."""

    def to_internal_value(self, data):
        """Преобразует данные внутреннего представления поля.
        Поле должно принимать данные в формате base64."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext: str = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов"""

    class Meta:
        model = Tag
        fields: Tuple[str] = ('id', 'name', 'color', 'slug')
        read_only_fields: Tuple[str] = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""

    class Meta:
        model = Ingredient
        fields: Tuple[str] = ('id', 'name', 'measurement_unit')
        read_only_fields: Tuple[str] = ('id', 'name', 'measurement_unit')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя User."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj: User) -> bool:
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False

    def create(self, validated_data: dict) -> User:
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields: Tuple[str] = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')
        read_only_fields: Tuple[str] = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')


class UserSubscriptionSerializer(UserSerializer):
    """Сериализатор для подписок."""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    def get_recipes_count(self, obj: User) -> int:
        return obj.recipes.count()


    class Meta(UserSerializer.Meta):
        model = User
        fields: Tuple[str] = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')
        read_only_fields: Tuple[str] = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов"""

    class Meta:
        model = Recipe
        fields: Tuple[str] = (
            'id',
            'name',
            'author',
            'tags',
            'text',
            'ingredients',
            'image',
            'cooking_time',
        )
        read_only_fields: Tuple[str] = (
            'id', 'author', 'tags',
        )


