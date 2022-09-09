from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe,
                     ShoppingCart, Recipe, TagInRecipe, Tag)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')

    @admin.display(description='in_favorite')
    def in_favorite(self, obj):
        return len(obj.in_favorites.all())


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class TagInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(TagInRecipe, TagInRecipeAdmin)
admin.site.register(IngredientInRecipe)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
