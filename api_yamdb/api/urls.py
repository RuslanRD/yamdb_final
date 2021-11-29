from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserGetTokenViewSet,
                    UserSignupViewSet, UserViewSet)

router = DefaultRouter()
router.register(r'^users', UserViewSet, basename='users')
router.register(r'^titles', TitleViewSet, basename='titles')
router.register(r'^genres', GenreViewSet, basename='genres')
router.register(r'^categories', CategoryViewSet, basename='comments')
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/token/', UserGetTokenViewSet.as_view(), name='token'),
    path('v1/auth/signup/', UserSignupViewSet.as_view(), name='signup'),
]
