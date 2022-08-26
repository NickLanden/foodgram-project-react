from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import (Favorite,
                     Ingredient,
                     IngredientInRecipe,
                     Recipe,
                     Tag)
from .permissions import IsAuthor
from .serializers import (FavoriteSerializer,
                          IngredientSerializer,
                          CreateIngredientsInRecipeSerializer,
                          CreateRecipeSerializer,
                          RecipeSerializer,
                          RecipeForFavoriteSerializer,
                          TagSerializer)
from .viewsets import CreateDestroyViewSet, CreateRetrieveDestroyViewSet


def get_object_or_400(klass, text_error, *args, **kwargs):
    queryset = klass.objects.all()
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise serializers.ValidationError(text_error)


class TagViewSet(ReadOnlyModelViewSet):
    """Viewset для вывода одного или сразу всех тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    lookup_field = 'id'


class CustomSearchFilter(SearchFilter):
    search_param = "name"


class IngredientViewSet(ReadOnlyModelViewSet):
    """Viewset для вывод одного или сразу всех ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    lookup_field = 'id'
    filter_backends = (CustomSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """ViewSet для обработки запросов, связанных с рецептами."""
    queryset = Recipe.objects.all()
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author',)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            self.permission_classes = (AllowAny,)
        elif self.action == 'create':
            self.permission_classes = (IsAuthenticated,)
        elif self.action == 'favorite':
            self.permission_classes = (IsAuthor,)
        elif self.action == 'destroy':
            self.permission_classes = (IsAuthor,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        elif self.action == 'create':
            return CreateRecipeSerializer
        elif self.action == 'favorite':
            return FavoriteSerializer

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, id=None):
        recipe = get_object_or_400(Recipe, 'Такого рецепта не существует!', pk=id)
        user = request.user
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe):
                raise serializers.ValidationError('Рецепт уже в избранном!')

            Favorite.objects.create(
                user=user,
                recipe=recipe
            )
            serializer = RecipeForFavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            favorite = get_object_or_400(Favorite, 'Рецепт не добавлен в избранное!', recipe=recipe, user=user)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class FavoriteViewSet(CreateDestroyViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def perform_create(self, serializer):
        recipe_id = self.kwargs['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = self.request.user
        if Favorite.objects.filter(user=user, recipe=recipe):
            raise serializers.ValidationError('Рецепт уже в избранном!')
        serializer.save(user=user, recipe=recipe)

    def perform_destroy(self, instance):
        if instance.user == self.request.user:
            instance.delete()
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
