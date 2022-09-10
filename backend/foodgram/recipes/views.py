import datetime
import os

from django.db.utils import IntegrityError
from django.http import HttpResponse
from django_filters import rest_framework as filters
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from foodgram import settings
from .filters import RecipeFilter
from .models import (Favorite,
                     Ingredient,
                     IngredientInRecipe,
                     ShoppingCart,
                     Recipe,
                     Tag)
from .permissions import IsAuthor
from .serializers import (FavoriteSerializer,
                          IngredientSerializer,
                          CreateRecipeSerializer,
                          RecipeSerializer,
                          RecipeForFavoriteSerializer,
                          TagSerializer)


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
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('author',)

    def get_queryset(self):
        queryset = Recipe.objects.all()

        if self.action == 'list':
            tags = self.request.query_params.get('tags')
            is_favorited = self.request.query_params.get('is_favorited')
            is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')

            if tags is not None:
                queryset = queryset.filter(tags__slug=tags)

            if is_favorited is not None:
                favorites = Favorite.objects.filter(user=self.request.user)
                recipes = []
                for f in favorites:
                    recipes.append(f.recipe.id)
                queryset = queryset.filter(id__in=recipes)

            if is_in_shopping_cart is not None:
                cart = ShoppingCart.objects.filter(user=self.request.user)
                recipes = []
                for c in cart:
                    recipes.append(c.recipe.id)
                queryset = queryset.filter(id__in=recipes)

        return queryset.order_by('-id')

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            self.permission_classes = (AllowAny,)
        elif self.action in (
                'create', 'shopping_cart', 'download_shopping_cart'):
            self.permission_classes = (IsAuthenticated,)
        elif self.action in ('favorite', 'destroy', 'partial_update'):
            self.permission_classes = (IsAuthor,)
        return super().get_permissions()

    def get_serializer_class(self):
        print(self.action)
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        elif self.action == 'create':
            return CreateRecipeSerializer
        elif self.action == 'favorite':
            return FavoriteSerializer
        elif self.action == 'partial_update':
            return CreateRecipeSerializer

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, id=None):
        recipe = get_object_or_400(
            Recipe,
            'Такого рецепта не существует!',
            pk=id
        )
        user = request.user
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe):
                raise serializers.ValidationError(
                    'Рецепт уже в избранном!')

            Favorite.objects.create(
                user=user,
                recipe=recipe
            )
            serializer = RecipeForFavoriteSerializer(recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            favorite = get_object_or_400(
                Favorite, 'Рецепт не добавлен в избранное!',
                recipe=recipe,
                user=user
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        file_path = os.path.join(
            settings.MEDIA_ROOT,
            'recipes/shopping_cart/',
            str(request.user)
        )

        os.makedirs(file_path, exist_ok=True)
        file = os.path.join(
            file_path, str(datetime.datetime.now()) + '.txt')

        user = request.user
        purchases = ShoppingCart.objects.filter(user=user)

        with open(file, 'w') as f:
            cart = dict()
            for purchase in purchases:
                ingredients = IngredientInRecipe.objects.filter(
                    recipe=purchase.recipe.id
                )
                for r in ingredients:
                    i = Ingredient.objects.get(pk=r.ingredient.id)
                    point_name = f'{i.name} ({i.measurement_unit})'
                    if point_name in cart.keys():
                        cart[point_name] += r.amount
                    else:
                        cart[point_name] = r.amount
            for name, amount in cart.items():
                f.write(f'* {name} - {amount}\n')

        with open(file, 'rb') as f:
            response = HttpResponse(
                f.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'inline; filename=' + file
            return response

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, id=None):
        recipe = get_object_or_400(
            Recipe, 'Такого рецепта не существует!', pk=id)

        if request.method == 'POST':

            try:
                ShoppingCart.objects.create(
                    user=request.user, recipe=recipe)
            except IntegrityError:
                error = 'Этот рецепт уже добавлен в список покупок!'
                return Response(
                    data={'errors': error},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = RecipeForFavoriteSerializer(
                recipe, context={'request': request}
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        else:
            cart = get_object_or_400(
                ShoppingCart,
                'Такого рецепта нет в вашем списке покупок!',
                user=request.user,
                recipe=recipe)
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
