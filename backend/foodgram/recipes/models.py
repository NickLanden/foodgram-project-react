from django.db import models

from colorfield.fields import ColorField

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name='Название тэга'
    )
    color = ColorField(unique=True)
    slug = models.SlugField(unique=True)

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
    name = models.CharField(max_length=128,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=128,
                                        verbose_name='Единица измерения')

    def __str__(self):
        return self.name

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
    cooking_time = models.IntegerField()

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


class RecipesTags(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        to=Tag,
        on_delete=models.CASCADE,
        verbose_name='Тэг',
    )

    def __str__(self):
        return f'{self.recipe}, {self.tag}'

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
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField()

    def __str__(self):
        return f'{self.recipe}, {self.ingredient}'

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe_id', 'ingredient_id'),
                name='unique_ingredients_recipes',
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    def __str__(self):
        return f'{self.user}, {self.recipe}'

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('user_id', 'recipe_id'),
                name='unique_favorites',
            )
        ]


class Purchase(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в корзине',
    )

    def __str__(self):
        return f'{self.user.username}, {self.recipe}'

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user_id', 'recipe_id'),
                name='unique_tags',
            )
        ]
