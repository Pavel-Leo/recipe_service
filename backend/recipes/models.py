from typing import List

from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

TEXT_SYMBOLS: int = 20


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        'Название ингредиента',
        max_length=200,
        blank=False,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
        blank=False,
    )

    class Meta:
        ordering: List[str] = ['-id']
        verbose_name: str = 'ингредиент'
        verbose_name_plural: str = 'ингредиенты'

    def __str__(self) -> str:
        return self.name[:TEXT_SYMBOLS]


class Tag(models.Model):
    """Модель тэгов."""

    name = models.CharField(
        'Название тэга',
        max_length=50,
        blank=False,
    )
    color = models.CharField(
        'Цвет тэга в HEX',
        max_length=20,
        blank=False,
        unique=True,
    )
    slug = models.SlugField(
        'Слаг тэга',
        max_length=100,
        blank=False,
        unique=True,
    )

    class Meta:
        ordering: List[str] = ['-id']
        verbose_name: str = 'тэг'
        verbose_name_plural: str = 'тэги'

    def __str__(self) -> str:
        return self.name[:TEXT_SYMBOLS]


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200,
        blank=False,
    )
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='recipes_images/',
        blank=True,
    )
    text = models.TextField(
        'Описание рецепта',
        blank=False,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(1),
            'Время приготовления должно быть больше 0',
        ],
    )

    class Meta:
        ordering: List[str] = ['-id']
        verbose_name: str = 'рецепт'
        verbose_name_plural: str = 'рецепты'

    def __str__(self) -> str:
        return self.name[:TEXT_SYMBOLS]


class RecipeIngredient(models.Model):
    """Модель для связи ингредиентов в рецептах с указанием количества."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепты',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Связанные ингредиенты',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиента',
        validators=[
            MinValueValidator(1),
            'Количество ингредиентов должно быть больше 0',
        ],
    )

    class Meta:
        ordering: List[str] = ['-id']
        verbose_name: str = 'Ингредиент рецепта'
        verbose_name_plural: str = 'Ингредиенты рецептов'
        constraints = models.UniqueConstraint(
            fields=('recipe', 'ingredient'),
            name='unique_recipe_ingredient',
        )

    def __str__(self) -> str:
        return self.ingredient.name[:TEXT_SYMBOLS]


class Favorite(models.Model):
    """Модель для добавления рецептов в избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering: List[str] = ['-id']
        verbose_name: str = 'избранный рецепт'
        verbose_name_plural: str = 'избранные рецепты'
        constraints = models.UniqueConstraint(
            fields=('user', 'recipe'),
            name='unique_favorite',
        )

    def __str__(self) -> str:
        return f'{self.user.username} добавил {self.recipe.name} в избранное'
