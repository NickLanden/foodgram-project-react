import base64

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from rest_framework import serializers

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
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favorited(self, instance):
        if Favorite.objects.filter(recipe=instance.id).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, instance):
        if instance.in_shopping_cart.filter(user=self.context['request'].user).exists():
            return True
        return False


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class TagSerializer2(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all()
    )
    name = serializers.ReadOnlyField()

    class Meta:
        model = Tag
        fields = ('id', 'name')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name='temp.' + ext
            )
        return super().to_internal_value(data)


def ingredients_update(instance, validated_data):
    ingredients = validated_data.pop('ingredients')
    new_ingredients = []

    for ingredient in ingredients:

        try:
            in_recipe = instance.ingredients_in.get(
                ingredient=ingredient['id'])
            new_ingredients.append(in_recipe)
            if in_recipe.amount != ingredient['amount']:
                in_recipe.amount = ingredient['amount']
                in_recipe.save()
                continue
            continue
        except ObjectDoesNotExist:
            ingredient_instance = Ingredient.objects.get(
                pk=ingredient['id'].id)
            amount = ingredient['amount']
            new_ing_in_recipe = IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient_instance,
                amount=amount
            )
            new_ingredients.append(new_ing_in_recipe)
            continue

    recipe_ingredients = instance.ingredients_in.all()
    if len(recipe_ingredients) != len(ingredients):
        for ing in recipe_ingredients:
            if ing not in new_ingredients:
                ing.delete()


def tags_update(instance, validated_data):
    tags = validated_data.pop('tags')
    new_tags = []

    for tag in tags:
        try:
            t = instance.tags_in.get(tag=tag)
            new_tags.append(t)
            continue
        except ObjectDoesNotExist:
            tag_instance = Tag.objects.get(pk=tag.id)
            new_tag_in_recipe = TagInRecipe.objects.create(
                recipe=instance,
                tag=tag_instance
            )
            new_tags.append(new_tag_in_recipe)
            continue

    recipe_tags = instance.tags_in.all()
    if len(recipe_tags) != len(tags):
        for t in recipe_tags:
            if t not in new_tags:
                t.delete()


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'name',
                  'image', 'text', 'cooking_time')

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data

    def create(self, validated_data):
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

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )

        ingredients_update(instance, validated_data)
        tags_update(instance, validated_data)

        instance.save()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('id',)


class RecipeForFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
