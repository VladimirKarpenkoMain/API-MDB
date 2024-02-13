from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .enums import UserRoles


class User(AbstractUser):
    """Класс пользователей."""
    username = models.CharField(max_length=150,
                                unique=True,
                                verbose_name='Имя пользователя',
                                db_index=True,
                                validators=[RegexValidator(regex=r'^[\w.@+-]+$',
                                                           message='Имя пользователя содержит недопустимый символ')])
    email = models.EmailField(max_length=254,
                              unique=True,
                              verbose_name='Электронная почта пользователя')

    first_name = models.CharField(max_length=150,
                                  verbose_name='Имя',
                                  blank=True)

    last_name = models.CharField(max_length=150,
                                 verbose_name='Фамилия',
                                 blank=True)

    bio = models.TextField(
        verbose_name='Биография',
        blank=True
    )

    role = models.CharField(
        max_length=20,
        verbose_name='Роль',
        choices=UserRoles.choices(),
        default=UserRoles.user.name
    )

    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return f"{self.username}"

    @property
    def is_admin(self):
        return self.role == UserRoles.admin.name

    @property
    def is_moderator(self):
        return self.role == UserRoles.moderator.name

    @property
    def is_user(self):
        return self.role == UserRoles.user.name
