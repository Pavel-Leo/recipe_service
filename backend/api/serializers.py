import base64
from typing import Dict, List, Tuple

from django.core.files.base import ContentFile
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField

from users.models import Subscription, User
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class Base64ImageField(serializers.ImageField):
    """Переопределяет поведение поля изображения."""

    def to_internal_value(self, data):
        """Преобразует данные внутреннего представления поля.
        Поле должно принимать данные в формате base64."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext: str = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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
        fields: Tuple[str] = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields: Tuple[str] = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class UserSubscriptionSerializer(UserSerializer):
    """Сериализатор для подписок."""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    def validate(self, data: Dict) -> Dict:
        author = self.instance
        user = self.context.get('request').user
        if Subscription.objects.filter(user=user, author=author).exists():
            raise ValidationError(
                detail='Подписка на автора уже существует!',
                code=status.HTTP_400_BAD_REQUEST,
            )

        if author == user:
            raise ValidationError(
                detail='Нельзя подписаться на себя!',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes_count(self, obj: User) -> int:
        return obj.recipes.count()

    def get_recipes(self, obj: User) -> List[Dict]:
        request = self.context.get('request')
        recipes = obj.recipes.all()
        serializer = RecipeShopCartSerializer(
            recipes, many=True, read_only=True, context={'request': request},
        )
        return serializer.data

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
        read_only_fields: Tuple[str] = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes_count',
            'recipes',
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


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецептов."""

    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = SerializerMethodField(method_name='get_ingredients')
    is_recipe_in_favorite = SerializerMethodField(
        read_only=True, method_name='get_is_recipe_in_favorite',
    )
    is_recipe_in_shopping_cart = SerializerMethodField(
        read_only=True, method_name='get_is_recipe_in_shopping_cart',
    )

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
            'is_recipe_in_favorite',
            'is_recipe_in_shopping_cart',
        )

    def get_ingredients(self, obj: Recipe) -> List:
        """Метод для получения списка ингредиентов."""
        ingredient_subquery = RecipeIngredient.objects.filter(
            recipe=OuterRef('pk'),
        ).values('amount')
        ingredients = obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
        ).annotate(amount=Subquery(ingredient_subquery))
        return ingredients

    def get_is_recipe_in_favorite(self, obj: Recipe) -> bool:
        """Метод для проверки наличия рецепта в избранном."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_recipe_in_shopping_cart(self, obj: Recipe) -> bool:
        """Метод для проверки наличия рецепта в списке покупок."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецептах."""

    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields: Tuple[str] = ('id', 'amount')


class RecipePostOrPatchSerializer(serializers.ModelSerializer):
    """Сериализатор для создания или обновления рецептов."""

    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(many=True)
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

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
        )

    def validate_ingredients(self, value: List[Dict]) -> List[Dict]:
        """Метод для валидации ингредиентов."""
        ingredients = value
        if ingredients:
            used_ingredients = []
            for ingr in ingredients:
                ingredient = get_object_or_404(Ingredient, id=ingr['id'])
                if ingredient in used_ingredients:
                    raise ValidationError('Ингредиенты не должны повторяться')
                if int(ingr['amount']) < 1:
                    raise ValidationError(
                        'Количество ингредиента не может быть меньше 1',
                    )
                used_ingredients.append(ingredient)
            return value
        else:
            raise ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент',
            )

    def validate_tags(self, value: List[Dict]) -> List[Dict]:
        """Метод для валидации тэгов."""
        tags = value
        if tags:
            used_tags = []
            for tag in tags:
                if tag in used_tags:
                    raise ValidationError('Тэги не должны повторяться')
                used_tags.append(tag)
            return value
        else:
            raise ValidationError('Рецепт должен содержать хотя бы один тэг')

    def create(self, validated_data: dict) -> Recipe:
        """Метод для создания рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        try:
            recipe: Recipe = Recipe.objects.create(**validated_data)
            recipe.tags.set(tags)
            for ingr in ingredients:
                ingredient = Ingredient.objects.get(id=ingr['id'])
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingr['amount'],
                )
        except Exception as e:
            raise ValidationError(str(e))
        return recipe

    def update(self, instance: Recipe, validated_data: dict) -> Recipe:
        """Метод для обновления рецепта."""
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time,
        )
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.clear()
            instance.tags.set(tags_data)
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            instance.ingredients.clear()
            for ingr in ingredients_data:
                ingredient = Ingredient.objects.get(id=ingr['id'])
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingr['amount'],
                )
        instance.save()
        return instance


class RecipeShopCartSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в списке покупок."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields: Tuple[str] = ('id', 'name', 'image', 'сooking_time')
        read_only_fields: Tuple[str] = ('id', 'name', 'image', 'сooking_time')
