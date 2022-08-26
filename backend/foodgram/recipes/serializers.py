from collections import OrderedDict
from rest_framework.relations import PKOnlyObject

from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators

from users.serializers import UserSerializer
from .models import (Favorite,
                     Ingredient,
                     IngredientInRecipe,
                     Recipe,
                     Tag,
                     TagInRecipe)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientInRecipeSerializer(
        source='ingredients_in', many=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        if Favorite.objects.filter(recipe=obj.id).exists():
            return True
        return False


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True)
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'measurement_unit', 'name', 'amount')


class TagSerializer2(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all()
    )
    name = serializers.ReadOnlyField()

    class Meta:
        model = Tag
        fields = ('id', 'name')


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), write_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'is_favorited', 'author', 'name', 'text', 'cooking_time')

    def create(self, validated_data):
        print(validated_data)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        user = self.context.get('request').user
        recipe = Recipe.objects.create(
            **validated_data, author=user)

        for ingredient in ingredients:
            ingredient_instance = Ingredient.objects.get(
                pk=ingredient['id'].id)
            amount = ingredient['amount']
            IngredientInRecipe.objects.create(
                    recipe=recipe,
                    ingredient=ingredient_instance,
                    amount=amount
                )

        recipe.tags.set(tags)
        return recipe

    def get_is_favorited(self, instance):
        if Favorite.objects.filter(recipe=instance.id).exists():
            return True
        return False


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('id',)


class RecipeForFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
