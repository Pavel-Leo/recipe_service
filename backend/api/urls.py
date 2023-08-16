from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    SubscribeViewSet,
    download_shopping_cart,
    FavoriteViewSet,
    ShoppingCartViewSet,
    UserViewSet,
)

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/', FavoriteViewSet.as_view(), name='favorite'),
    path('recipes/download_shopping_cart/', download_shopping_cart, name='download_shopping_cart'),
    path('recipes/<int:recipe_id>/shopping_cart/', ShoppingCartViewSet.as_view(), name='shopping_cart'),
    path('users/<int:user_id>/subscribe/', SubscribeViewSet.as_view(), name='subscribe'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
