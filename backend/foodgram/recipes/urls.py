from django.urls import include, path

from rest_framework import routers

from .views import (FavoriteViewSet,
                    IngredientViewSet,
                    RecipeViewSet,
                    TagViewSet)

app_name = 'recipes'

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(
    r'recipes/(?P<id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite'
)

urlpatterns = [
    path('', include(router.urls))
]
