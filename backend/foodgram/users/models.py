from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'user'),
        (ADMIN, 'admin')
    ]
    username = models.CharField(max_length=150,
                                unique=True,
                                verbose_name='Имя пользователя')
    email = models.EmailField(max_length=254,
                              unique=True,
                              verbose_name='Адрес электронной почты')
    first_name = models.CharField(max_length=150,
                                  null=False,
                                  blank=False,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=150,
                                 null=False,
                                 blank=False,
                                 verbose_name='Фамилия')
    role = models.TextField(choices=ROLE_CHOICES,
                            default=USER,
                            verbose_name='Роль пользователя')

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор рецептов',
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('author_id', 'subscriber_id'),
                name='unique_subscriptions',
            )
        ]

    def __str__(self):
        return f'{self.author} - {self.subscriber}'
