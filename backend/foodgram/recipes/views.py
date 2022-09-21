from django.db.utils import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import CustomSearchFilter, RecipeFilter
from .models import (Favorite,
                     Ingredient,
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
from .download_shopping_cart import download_shopping_cart


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
    filterset_class = RecipeFilter

    def get_permissions(self):
        print(self.action)
        if self.action in ('list', 'retrieve'):
            self.permission_classes = (AllowAny,)
        elif self.action in (
                'create', 'shopping_cart', 'download_shopping_cart'):
            self.permission_classes = (IsAuthenticated,)
        elif self.action in ('favorite', 'destroy', 'partial_update'):
            self.permission_classes = (IsAuthor,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        elif self.action == 'create':
            return CreateRecipeSerializer
        elif self.action == 'favorite':
            return FavoriteSerializer
        elif self.action == 'partial_update':
            return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

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
        return download_shopping_cart(request)

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
