from rest_framework import viewsets

from .models import Recipe, Tag
from .serializers import RecipeSerializer, TagSerializer
from .viewsets import ListRetrieveViewSet


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
