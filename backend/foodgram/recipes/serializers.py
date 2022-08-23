from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators

from users.serializers import UserSerializer
from .models import (Favorite,
                     Ingredient,
                     IngredientInRecipe,
                     Recipe,
                     Tag)


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
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class TagSerializer2(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    name = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class CreateRecipeSerializer(serializers.ModelSerializer):
    # ingredients = CreateIngredientsInRecipeSerializer(many=True)
    # tags = serializers.PrimaryKeyRelatedField(
    #     many=True, queryset=Tag.objects.all())
    tags = TagSerializer2(many=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'name', 'text', 'cooking_time')

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['ingredients'] = IngredientInRecipeSerializer(
    #         instance.ingredients, many=True).data
    #     print(representation)
    #     return representation

    # def create(self, validated_data):
    #     print(validated_data)
    #     tags = validated_data.pop('tags')
        # ingredients = validated_data.pop('ingredients')
        # print(ingredients)
        # print(validated_data)
        # user = self.context.get('request').user
        # recipe = Recipe.objects.create(
        #     **validated_data, author=user)
        # for ingredient in ingredients:
        #     print(ingredient['ingredient'])
        #     ingredient_instance = Ingredient.objects.get(
        #         pk=ingredient['ingredient'])
        #     amount = ingredient['amount']
        #     IngredientInRecipe.objects.create(
        #         recipe=recipe,
        #         ingredient=ingredient_instance,
        #         amount=amount
        #     )
        # return recipe


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('id',)
