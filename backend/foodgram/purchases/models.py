from django.db import models

from recipe.models import Recipe
from users.models import User


class Purchase(models.Model):
    user_id = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
    )
    recipe_id = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
    )
