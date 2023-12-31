from typing import List

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()

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
        ordering: List[str] = ['name']
        verbose_name: str = 'ингредиент'
        verbose_name_plural: str = 'ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient',
            ),
        ]

    def __str__(self) -> str:
        return self.name[:TEXT_SYMBOLS]


class Tag(models.Model):
    """Модель тэгов."""

    name = models.CharField(
        'Название тэга',
        max_length=50,
        blank=False,
        unique=True,
    )
    color = models.CharField(
        'Цвет тэга в HEX',
        max_length=7,
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
        blank=False,
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        blank=False,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='tags',
        db_index=True,
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(
                1,
                message='Время приготовления должно быть больше 0',
            ),
            MaxValueValidator(
                4320,
                message='Время приготовления не должно превышать 4320 минут',
            ),
        ],
    )

    class Meta:
        ordering: List[str] = ['-id']
        verbose_name: str = 'рецепт'
        verbose_name_plural: str = 'рецепты'

    def favorite_count(self) -> int:
        return self.favorites.count()

    def __str__(self) -> str:
        return self.name[:TEXT_SYMBOLS]


class RecipeIngredient(models.Model):
    """Модель для связи ингредиентов в рецептах с указанием количества."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
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
            MinValueValidator(
                1,
                message='Количество ингредиентов должно быть больше 0',
            ),
            MaxValueValidator(
                100, message='Количество ингредиентов не должно превышать 100',
            ),
        ],
    )

    class Meta:
        ordering: List[str] = ['-id']
        verbose_name: str = 'Количество ингредиента'
        verbose_name_plural: str = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            ),
        ]

    def __str__(self) -> str:
        return self.ingredient.name[:TEXT_SYMBOLS]


class CommonAbstact(models.Model):
    """Модель абстрактного класса для Favorite и ShoppingCart."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return (
            f'{self.user.username} добавил'
            f' {self.recipe.name} в {self._meta.verbose_name}'
        )


class Favorite(CommonAbstact):
    """Модель для добавления рецептов в избранное."""

    class Meta:
        ordering: List[str] = ['-id']
        verbose_name: str = 'избранный рецепт'
        verbose_name_plural: str = 'избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite',
            ),
        ]
        default_related_name = 'favorites'


class ShoppingCart(CommonAbstact):
    """Модель для списка покупок."""

    class Meta:
        ordering: List[str] = ['-id']
        verbose_name: str = 'cписок для покупок'
        verbose_name_plural: str = 'cписок для покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart',
            ),
        ]
        default_related_name = 'carts'
