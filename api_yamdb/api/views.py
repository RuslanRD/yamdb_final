from django.core.mail import get_connection, EmailMessage
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import (
    LimitOffsetPagination, PageNumberPagination
)
from rest_framework import (
    decorators, status, filters, response, viewsets, permissions, generics
)

from reviews.models import Category, Genre, Title, Review
from users.models import User
from .filters import TitleFilter
from .permissions import (
    AdminOrReadOnly, Signup, IsAdmin, ReviewCommentPermission
)
from .serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer, UserSerializer,
    UserSignupSerializer, UserGetTokenSerializer, ReviewSerializer,
    CommentSerializer, TitleListSerializer
)
from .mixins import CreateDestroyListViewSet
from django.conf import settings


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [IsAdmin, ]
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username', )

    @decorators.action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def me(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(instance=user)
            return response.Response(
                serializer.data, status=status.HTTP_200_OK
            )
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop('role', False)
        self.perform_update(serializer)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class UserSignupViewSet(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [Signup]

    @classmethod
    def get_extra_actions(cls):
        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )
        token = default_token_generator.make_token(user)
        email = serializer.validated_data['email']
        with get_connection() as connection:
            EmailMessage(
                'Получение JWT-токена',
                f'Ваш код подтверждения: {token}',
                settings.EMAIL_HOST_USER,
                [email, ],
                connection=connection
            ).send()
        return response.Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )


class UserGetTokenViewSet(generics.CreateAPIView):
    serializer_class = UserGetTokenSerializer
    permission_classes = [Signup]

    @classmethod
    def get_extra_actions(cls):
        return []

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(
                User,
                username=serializer.validated_data['username']
            )
            refresh = RefreshToken.for_user(user)
            data = {'token': str(refresh.access_token)}
            return response.Response(data, status=status.HTTP_201_CREATED)
        return response.Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TitleListSerializer
        return TitleSerializer


class GenreViewSet(CreateDestroyListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    permission_classes = (AdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(CreateDestroyListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = (AdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        ReviewCommentPermission, permissions.IsAuthenticatedOrReadOnly
    ]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        new_queryset = title.reviews.all().order_by('-pub_date')
        return new_queryset

    def perform_create(self, serializer):

        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        ReviewCommentPermission, permissions.IsAuthenticatedOrReadOnly
    ]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        new_queryset = review.comments.all().order_by('-pub_date')
        return new_queryset

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return serializer.save(author=self.request.user, review=review)
