import datetime
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

import os

from .models import (Favorite, Ingredient, IngredientsRecipes,
                     Purchase, Recipe, Tag)
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          PurchaseSerializer, RecipeSerializer, TagSerializer)
from foodgram import settings
from .viewsets import CreateDestroyViewSet, ListRetrieveViewSet


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        recipe = Recipe.objects.get(pk=pk)

        if request.method == 'POST':
            Purchase.objects.create(user=request.user, recipe=recipe)
            serializer = PurchaseSerializer(
                recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            purchase = get_object_or_404(Purchase, user=request.user, recipe=recipe)
            purchase.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        file_path = os.path.join(
            settings.MEDIA_ROOT,
            'recipes/shopping_cart/',
            str(request.user)
        )

        os.makedirs(file_path, exist_ok=True)
        file = os.path.join(file_path, str(datetime.datetime.now()) + '.txt')

        user = request.user
        purchases = Purchase.objects.filter(user=user)
        with open(file, 'w') as f:
            cart = dict()
            for purchase in purchases:
                ingredients = IngredientsRecipes.objects.filter(
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
            response = HttpResponse(f.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'inline; filename=' + file
            return response


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class FavoriteViewSet(CreateDestroyViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
