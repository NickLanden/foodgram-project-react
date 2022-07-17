from rest_framework import serializers

from .models import Recipe, Tag


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
