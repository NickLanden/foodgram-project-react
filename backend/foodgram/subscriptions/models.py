from django.db import models

from users.models import User


class Subscription(models.Model):
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
    )
    subscriber = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
    )
