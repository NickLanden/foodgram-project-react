from rest_framework import serializers

from .models import (Favorite, Ingredient, IngredientsRecipes,
                     Purchase, Recipe, Tag)
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, ingredient):
        return IngredientsRecipes.objects.get(pk=ingredient.id).amount


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()

    # is_in_shopping_cart =

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, instance):
        if Favorite.objects.filter(recipe=instance.id).exists():
            return True
        return False


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite


class PurchaseSerializer(serializers.ModelSerializer):
    # cooking_time = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    # def get_cooking_time(self, recipe):
    #     return Recipe.objects.get(pk=recipe.id).cooking_time
