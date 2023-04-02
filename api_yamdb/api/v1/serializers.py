from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        exclude = ('id',)
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения модели Title."""
    genre = GenreSerializer(many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        fields = '__all__'
        model = Title


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания модели Title."""
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализер отзывов."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        exclude = ('title',)

    def get_title(self):
        request = self.context.get('request')
        return get_object_or_404(
            Title,
            pk=request.parser_context.get('kwargs').get('title_id')
        )

    def validate(self, attrs):
        if self.context.get('request').method == 'POST':
            user = self.context.get('request').user
            if Review.objects.filter(author=user, title=self.get_title()):
                raise serializers.ValidationError(
                    'Вы не можете создать два отзыва на одно произведение.'
                )
        return super().validate(attrs)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев к отзывам."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        exclude = ('review',)


class AdminSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User.
    Права доступа: Администратор.
    """

    class Meta:
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")
        model = User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User.
    Права доступа: Любой авторизованный пользователь.
    """

    class Meta:
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")
        model = User
        read_only_fields = ('role',)


class TokenSerializer(serializers.Serializer):
    """Сериализатор получения JWT-токена"""

    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class GenerateCodeSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователей и выдачи токенов"""

    class Meta:
        fields = ("username", "email")
        model = User

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError('Служебное имя. Выберите другое')
        return data
