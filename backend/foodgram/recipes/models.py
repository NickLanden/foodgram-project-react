from django.db import models

from colorfield.fields import ColorField

from users.models import User
from .validators import validate_integer_greater_zero


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тэга'
    )
    color = ColorField(unique=True, verbose_name='Цвет', null=True)
    slug = models.SlugField(unique=True, null=True, max_length=200)

    def __str__(self):
        return self.name

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
    name = models.CharField(max_length=200,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Единица измерения')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
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
        related_name='recipes',
    )
    name = models.CharField(max_length=200,
                            verbose_name='Название рецепта')
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        blank=True,
    )
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        to=Tag,
        through='TagInRecipe',
        verbose_name='Тэги',
    )
    cooking_time = models.IntegerField(
        validators=[validate_integer_greater_zero]
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'name'),
                name='unique_recipes',
            )
        ]


class TagInRecipe(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='tags_in'
    )
    tag = models.ForeignKey(
        to=Tag,
        on_delete=models.CASCADE,
        verbose_name='Тэг',
        related_name='in_recipe'
    )

    def __str__(self):
        return f'{self.recipe}, {self.tag}'

    class Meta:
        verbose_name = 'Тэг на рецепте'
        verbose_name_plural = 'Тэги на рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe_id', 'tag_id'),
                name='unique_recipes_tags',
            )
        ]


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in'
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name='in_recipe'
    )
    amount = models.IntegerField(
        validators=[validate_integer_greater_zero]
    )

    def __str__(self):
        return f'{self.recipe}, {self.ingredient}'

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe_id', 'ingredient_id'),
                name='unique_recipes_ingredients',
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='in_favorites'
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user_id', 'recipe_id'),
                name='unique_favorites',
            )
        ]
