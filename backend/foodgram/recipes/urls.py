from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, TagViewSet, RecipeViewSet

app_name = 'recipes'

router = routers.DefaultRouter()
router.register('recipes',
                RecipeViewSet)
router.register('tags',
                TagViewSet)
router.register('ingredient',
                IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
