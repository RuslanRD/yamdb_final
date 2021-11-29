from django.shortcuts import get_object_or_404
from django.core.validators import RegexValidator
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers, validators

from users.models import User
from reviews.models import Genre, Category, Comment, Title, Review


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    score = serializers.IntegerField()

    def validate(self, attrs):
        title = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user.id
        message = 'Author review is alredy exist'
        if (not self.instance
                and Review.objects.filter(
                    title=title, author=author).exists()):
            raise serializers.ValidationError(message)
        return attrs

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
        read_only_fileds = ('title', 'review')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
        read_only_fields = ('author', 'review')


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(
            r'^[\w.@+-_]+$',
            (
                ('Имя может содержать латинские буквы, цифры и символы'),
                ('@, ., +, -, _')
            )
        ),
            validators.UniqueValidator(
                queryset=User.objects.all(),
                message='Данное имя занято!'
        )
        ]
    )
    email = serializers.EmailField(max_length=254)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise validators.ValidationError(
                f'Пользователь с почтой {value} уже существует!'
            )
        return value


class UserSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=None,
        min_length=None,
        allow_blank=False,
        required=True,
        validators=[
            validators.UniqueValidator(
                queryset=User.objects.all(),
                message='A user with that email already exists.'
            )
        ],
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть "me".'
            )
        return value


class UserGetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(max_length=150, required=True)

    def validate(self, data):
        token = data['confirmation_code']
        user = get_object_or_404(User, username=data['username'])
        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError(
                'Неверное имя пользователя или код подтверждения'
            )
        return data


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(
        validators=[RegexValidator(
            r'^[-a-zA-Z0-9_]+$',
            (
                ('Имя "slug" может содержать только латинские буквы и цифры')
            )
        ),
            validators.UniqueValidator(
                queryset=Genre.objects.all(),
                message='Данное имя занято!'
        )
        ]
    )
    name = serializers.CharField(required=False)

    class Meta:
        model = Genre
        exclude = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.CharField(
        validators=[RegexValidator(
            r'^[-a-zA-Z0-9_]+$',
            (
                ('Имя "slug" может содержать только латинские буквы и цифры')
            )
        ),
            validators.UniqueValidator(
                queryset=Category.objects.all(),
                message='Данное имя занято!'
        )
        ]
    )
    name = serializers.CharField(required=False)

    class Meta:
        model = Category
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    genre = serializers.SlugRelatedField(
        many=True,
        required=True,
        queryset=Genre.objects.all(),
        slug_field='slug'
    )
    year = serializers.IntegerField(required=True)
    category = serializers.SlugRelatedField(
        required=True,
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        model = Title
        exclude = ('author', )


class TitleListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=Title.objects.all(),
            message='Данное имя занято!'
        )
        ]
    )
    genre = GenreSerializer(many=True)
    year = serializers.IntegerField(required=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        exclude = ('author', )
