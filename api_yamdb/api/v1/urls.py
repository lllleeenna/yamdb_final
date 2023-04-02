from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import (CategoryViewSet, CommentsViewSet, GenreViewSet,
                          ReviewsViewSet, TitleViewSet, UserViewSet, signup,
                          get_token)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet, basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet, basename='comments'
)
router_v1.register(r'users', UserViewSet)

url_auth = [
    path('signup/', signup, name='signup'),
    path('token/', get_token, name='get_token')
]

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(url_auth)),
]
