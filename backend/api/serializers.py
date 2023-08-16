from typing import Tuple

from ast import Tuple
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields: Tuple[str] = ('id', 'name', 'color', 'slug')