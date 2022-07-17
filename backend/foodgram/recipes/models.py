from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name='Название тэга'
    )
    color = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'color', 'slug'),
                name='unique_tags',
            )
        ]


class Ingredient(models.Model):
    name = models.CharField(max_length=128,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=128,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Игредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredients',
            )
        ]


class Recipe(models.Model):
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.CharField(max_length=128,
                            verbose_name='Название рецепта')
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        blank=True,
    )
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through='IngredientsRecipes',
        verbose_name='Игредиенты',
    )
    tags = models.ManyToManyField(
        to=Tag,
        through='RecipesTags',
        verbose_name='Тэги',
    )
    cooking_time = models.FloatField()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'name'),
                name='unique_recipes',
            )
        ]


class RecipesTags(models.Model):
    recipe_id = models.ForeignKey(
        to=Recipe,
        on_delete=models.SET_NULL,
    )
    tag_id = models.ForeignKey(
        to=Tag,
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        verbose_name = 'Тэг на рецепте'
        verbose_name_plural = 'Тэги на рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe_id', 'tag_id'),
                name='unique_tags',
            )
        ]


class IngredientsRecipes(models.Model):
    recipe_id = models.ForeignKey(
        to=Recipe,
        on_delete=models.SET_NULL,
    )
    ingredients_id = models.ForeignKey(
        to=Ingredient,
        on_delete=models.DO_NOTHING,
    )
    amount = models.FloatField()

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe_id', 'ingredients_id'),
                name='unique_ingredients_recipes',
            )
        ]


class Favorites(models.Model):
    user_id = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
    )
    recipe_id = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('user_id', 'recipe_id'),
                name='unique_favorites',
            )
        ]
