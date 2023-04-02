from django.contrib import admin

from users.models import User
from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title


class TitleAdmin(admin.ModelAdmin):
    """Класс для работы с произведениями в админ-панели."""
    list_display = ('pk', 'name', 'year', 'description', 'category',)
    list_editable = ('category',)
    search_fields = ('name',)
    list_filter = ('year', 'category',)
    empty_value_display = '-пусто-'


class UserAdmin(admin.ModelAdmin):
    """Класс для работы с пользователями в админ-панели."""
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'bio', 'role')
    search_fields = ('username', 'email')
    list_filter = ('role',)
    empty_value_display = '-пусто-'


class GenreAdmin(admin.ModelAdmin):
    """Класс для работы с жанрами в админ-панели."""

    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class CategoryAdmin(admin.ModelAdmin):
    """Класс для работы с категориями в админ-панели."""

    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class ReviewAdmin(admin.ModelAdmin):
    """Класс для рабоыт с отзывами в админ-панели."""
    list_display = ('title', 'author', 'text', 'score', 'pub_date')
    search_fields = ('text', )


class CommentsAdmin(admin.ModelAdmin):
    """Класс для рабоыт с комментариями в админ-панели."""
    list_display = ('review', 'author', 'text', 'pub_date')
    search_fields = ('text', )


admin.site.register(User, UserAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(GenreTitle)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentsAdmin)
