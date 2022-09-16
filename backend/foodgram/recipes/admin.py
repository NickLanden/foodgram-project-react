from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe,
                     ShoppingCart, Recipe, TagInRecipe, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'in_favorite')
    list_filter = ('name', 'author', 'tags')

    def in_favorite(self, obj):
        return len(obj.in_favorites.all())


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(TagInRecipe)
class TagInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Tag)
admin.site.register(IngredientInRecipe)
