from rest_framework import viewsets

from .models import Favorite, Ingredient, Recipe, Tag
from .serializers import FavoriteSerializer, IngredientSerializer, RecipeSerializer, TagSerializer
from .viewsets import CreateDestroyViewSet, ListRetrieveViewSet


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class FavoriteViewSet(CreateDestroyViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
