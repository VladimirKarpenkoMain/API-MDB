from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

User = get_user_model()


class Category(models.Model):
    """ Класс категории"""
    name = models.CharField(max_length=256,
                            verbose_name='Категория',
                            db_index=True)

    slug = models.SlugField(max_length=50,
                            validators=[RegexValidator(regex=r'^[-a-zA-Z0-9_]+$',
                                                       message='Slug категории содержит недопустимый символ')],
                            unique=True,
                            verbose_name='Slug')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """ Класс жанра """
    name = models.CharField(max_length=256,
                            verbose_name='Жанр',
                            db_index=True)

    slug = models.SlugField(max_length=50,
                            validators=[RegexValidator(regex=r'^[-a-zA-Z0-9_]+$',
                                                       message='Slug жанра содержит недопустимый символ')],
                            unique=True,
                            verbose_name='Slug')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """ Класс произведения """
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name='Категория',
                                 related_name='title', null=True)

    genre = models.ManyToManyField(Genre, verbose_name='Жанр', through='GenreTitle')

    name = models.CharField(max_length=256,
                            verbose_name='Название',
                            db_index=True)

    year = models.PositiveIntegerField(verbose_name='Год выпуска',
                                       db_index=True,
                                       validators=[
                                           MinValueValidator(0, message='Значение года не может быть отрицательным'),
                                           MaxValueValidator(int(datetime.now().year),
                                                             message='Значение года не может быть больше нынешнего')])

    description = models.TextField(verbose_name="Описание", blank=True)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'name')

    def __str__(self):
        return self.name[:30]


class GenreTitle(models.Model):
    """ Вспомогательный класс, связывающий жанры и произведения """

    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )

    class Meta:
        verbose_name = 'Соответствие жанра и произведения'
        verbose_name_plural = 'Таблица соответствия жанров и произведений'
        ordering = ('id',)

    def __str__(self):
        return f'{self.title} принадлежит жанру/ам {self.genre}'


class Review(models.Model):
    """ Класс обзора """
    text = models.TextField(verbose_name='Отзыв')
    author = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE, related_name='reviews')
    score = models.PositiveIntegerField(verbose_name='Оценка', db_index=True,
                                        validators=[MinValueValidator(1, message='Введенная оценка ниже допустимой'),
                                                    MaxValueValidator(10, message='Введенная оценка выше допустимой')])
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Время публикации', db_index=True)
    title = models.ForeignKey(Title, on_delete=models.CASCADE, verbose_name='Произведение', related_name='reviews')

    class Meta:
        verbose_name = 'Обзор'
        verbose_name_plural = 'Обзоры'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_author_title'
            ),
        )

    def __str__(self):
        return self.text[:50]


class Comment(models.Model):
    """ Класс комментария """
    text = models.TextField(verbose_name='Комментарий')
    author = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, verbose_name='Обзор', related_name='comments')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Время публикации', db_index=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text[:15]
