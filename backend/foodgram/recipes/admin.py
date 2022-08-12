from django.contrib import admin

from .models import (Ingredient, RecipesIngredients,
                     Recipe, RecipesTags, Tag)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class RecipesTagsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(RecipesTags, RecipesTagsAdmin)
admin.site.register(RecipesIngredients)
