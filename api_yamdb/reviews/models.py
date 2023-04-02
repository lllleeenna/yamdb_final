
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from reviews.validators import validate_year
from users.models import User


class Category(models.Model):
    """Модель Категории."""
    name = models.CharField(
        max_length=256,
        verbose_name='Категория',
        help_text='Укажите категорию',
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        help_text='Укажите адрес',
        unique=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель Жанры."""
    name = models.CharField(
        max_length=256,
        verbose_name='Жанр',
        help_text='Укажите жанр',
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        help_text='Укажите адрес',
        unique=True
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель Произведения."""
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведение',
        help_text='Введите название произведения',
        unique=True
    )
    year = models.PositiveIntegerField(
        verbose_name='Год выпуска произведения',
        help_text='Введите год выпуска',
        db_index=True,
        validators=[validate_year]
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанры произведения',
        help_text='Укажите жaнры'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория произведения',
        help_text='Укажите категорию',
        null=True
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        help_text='Введите текст описания',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель для связи id произведения и id его жанра."""
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Жанр и произведение'
        verbose_name_plural = 'Жанры и произведения'

    def __str__(self):
        return f'Жанр: {self.genre}, произведение: {self.title}'


class Review(models.Model):
    """Модель отзывы на произведение."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации отзыва'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = [
            UniqueConstraint(fields=['title', 'author'], name='unique_review')
        ]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """Модель комментарии к отзывам."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации комментария'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]
