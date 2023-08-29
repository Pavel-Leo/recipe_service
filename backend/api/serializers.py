import base64
from typing import Any, Dict, List, Tuple

from api.validators import check_username
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer as DjoserCreateSerializer
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import UniqueValidator
from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Переопределяет поведение поля изображения."""

    def to_internal_value(self, data: str) -> Any:
        """Преобразует данные внутреннего представления поля.
        Поле должно принимать данные в формате base64."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext: str = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserCreateSerializer(DjoserCreateSerializer):
    """Сериализатор для создания пользователя."""

    email = serializers.EmailField(
        max_length=254,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким email уже существует!',
            ),
        ],
    )
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким username уже существует!',
            ),
            User.username_validator,
            check_username,
        ],
    )
    password = serializers.CharField(
        write_only=True,
    )
    first_name = serializers.CharField(
        max_length=150,
    )
    last_name = serializers.CharField(
        max_length=150,
    )

    class Meta:
        model = User
        fields: Tuple[str] = (
            'id',
            'email',
            'username',
            'password',
            'first_name',
            'last_name',
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя User."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj: User) -> bool:
        """Метод для проверки подписан ли текущий пользователь на автора."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False

    class Meta:
        model = User
        fields: Tuple[str] = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов"""

    class Meta:
        model = Tag
        fields: Tuple[str] = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""

    class Meta:
        model = Ingredient
        fields: Tuple[str] = ('id', 'name', 'measurement_unit')


class RecipeCartFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в списке покупок и избранном."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields: Tuple[str] = ('id', 'name', 'image', 'cooking_time')


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок на автора."""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields: Tuple[str] = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes_count',
            'recipes',
        )

    def get_is_subscribed(self, obj: User) -> bool:
        """Метод для проверки подписан ли текущий пользователь на автора."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False

    def get_recipes_count(self, obj: User) -> int:
        """Метод для получения количества рецептов автора."""
        return obj.recipes.count()

    def get_recipes(self, obj: User) -> List[Dict]:
        """Метод для получения рецептов автора."""
        request = self.context.get('request')
        limit = int(request.query_params.get('recipes_limit', '5'))
        recipes = obj.recipes.all()[:limit]
        return RecipeCartFavoriteSerializer(many=True).to_representation(
            recipes,
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецептах."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects,
        source='ingredient.id',
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )
    amount = serializers.IntegerField(
        min_value=1,
    )

    class Meta:
        model = RecipeIngredient
        fields: Tuple[str] = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецептов."""

    author = UserSerializer(read_only=True)
    image = serializers.ReadOnlyField(source='image.url')
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients',
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields: Tuple[str] = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj: Recipe) -> bool:
        """Метод для проверки наличия рецепта в избранном."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        """Метод для проверки наличия рецепта в списке покупок."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.carts.filter(user=user).exists()
        return False


class RecipePostOrPatchSerializer(RecipeGetSerializer):
    """Сериализатор для создания или обновления рецептов.
    Расширяет родительский класс RecipeGetSerializer, метод create и update
    наследуется от serializers.ModelSerializer родителя RecipeGetSerializer.
    """
    image = Base64ImageField()
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    cooking_time = serializers.IntegerField(min_value=1)

    def create(self, validated_data: dict) -> Recipe:
        """Метод для создания рецепта."""
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = super().create(validated_data)
        for ingr in ingredients:
            ingredient = ingr['ingredient']['id']
            amount = ingr['amount']
            recipe.ingredients.add(
                ingredient,
                through_defaults={'amount': amount},
            )
        return recipe

    def update(self, instance: Recipe, validated_data: dict) -> Recipe:
        """Метод для обновления рецепта."""
        ingredients = validated_data.pop('recipe_ingredients', None)
        recipe = super().update(instance, validated_data)
        for ingr in ingredients:
            ingredient = ingr['ingredient']['id']
            amount = ingr['amount']
            recipe.ingredients.add(
                ingredient, through_defaults={'amount': amount},
            )
        return recipe

    def validate_ingredients(self, value: List[Dict]) -> List[Dict]:
        """Метод для валидации ингредиентов."""
        ingredients = value
        ingredients_set = set(
            ingr.get('ingredient').get('id') for ingr in ingredients
        )
        if len(ingredients_set) != len(ingredients):
            raise ValidationError('Ингредиенты не должны повторяться')
        if any(int(ingr['amount']) < 1 for ingr in ingredients):
            raise ValidationError(
                'Количество ингредиента не может быть меньше 1',
            )
        return value
