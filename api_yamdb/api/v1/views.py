from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title
from users.models import User

from api.v1.filters import TitleFilter
from api.v1.mixins import CreateListDestroyViewSet
from api.v1.permissions import (IsAdmin, IsAdminOrReadOnly,
                                IsAuthorAdminModeratorOrReadOnly)
from api.v1.serializers import (AdminSerializer, CategorySerializer,
                                CommentSerializer, GenerateCodeSerializer,
                                GenreSerializer, ReviewSerializer,
                                TitleCreateSerializer, TitleSerializer,
                                TokenSerializer, UserSerializer)


class CategoryViewSet(CreateListDestroyViewSet):
    """Получение списка категорий, создание и удаление категории."""
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    """Получение списка жанров, создание и удаление жанра."""
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Получение списка произведений, одного произведения.
    Создание, изменение и удаление произведения.
    """
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return TitleSerializer
        return TitleCreateSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    """
    Получение списка отзывов, одного отзыва. Создание отзыва.
    Изменение и удаление отзыва.
    """

    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )

    def get_queryset(self):
        return self.get_title().reviews.all()


class CommentsViewSet(viewsets.ModelViewSet):
    """
    Получение списка комментариев к отзыву, одного комментария.
    Создание комментария. Изменение и удаление комментария.
    """

    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthorAdminModeratorOrReadOnly, )

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )

    def get_queryset(self):
        return self.get_review().comments.all()


class UserViewSet(viewsets.ModelViewSet):
    """Получение всех пользователей, добавление пользователя администратором.
    Получение, изменение и удаление пользователя по username администратором.
    Получение и изменение данных своей учетной записи пользователем.
    """
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = (IsAdmin, )
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ['username', ]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

    def perform_create(self, serializer):
        if not serializer.validated_data.get('role'):
            serializer.validated_data['role'] = 'user'
        User.objects.create_user(**serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        url_path='me',
        methods=['get', 'patch'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def show_user_profile(self, request):
        if request.method == "GET":
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "PATCH":
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    """Получение кода подтверждения на переданный email.
    Получение кода подтверждения уже зарегистрированному пользователю.
    """
    serializer = GenerateCodeSerializer(data=request.data)
    username = request.data.get('username')
    email = request.data.get('email')
    try:
        user = User.objects.get(username=username, email=email)
    except ObjectDoesNotExist:
        user = None
    if user:
        send_confirmation_code(user)
        message = ('Данный пользователь уже зарегистрирован.'
                   'Сообщение с кодом отправлено на почту.')
        return Response(message, status=status.HTTP_200_OK)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        username = serializer.validated_data["username"]
        user = get_object_or_404(User, username=username)
        send_confirmation_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def get_token(request):
    """Получение JWT-токена в обмен на username и confirmation code."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data["username"]
    code = serializer.validated_data["confirmation_code"]
    user = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user, code):
        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_confirmation_code(user):
    """Получение кода и отправка письма."""
    confirmation_code = default_token_generator.make_token(user)
    return send_mail(
        'Ваш код подтверждения',
        f'Код подтверждения для {user.username} : {confirmation_code}.',
        'from@yambd.com',
        [user.email],
        fail_silently=False,
    )
