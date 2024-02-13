from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api import serializers
from reviews.models import Category, Genre, Review, Title

from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissions import (AnonimReadOnly,
                          IsAuthorOrIsModeratorOrIsAdminOrIsSuperUserOnly,
                          IsSuperUserOrIsAdminOnly)
from .utilities import sent_confirmation_code

User = get_user_model()


class UserCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """ Вьюсет для создания объекта класса User """
    serializer_class = serializers.UserCreateSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """ Создаёт объект модели User и отправляет на почту
        код подтверждения """
        serializer = serializers.UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(**serializer.validated_data)
        confirmation_code = default_token_generator.make_token(user)
        sent_confirmation_code(
            email=user.email,
            confirmation_code=confirmation_code
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserReceiveTokenViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """ Вьюсет для получения пользователем JWT-токена """
    serializer_class = serializers.UserReceiveTokenSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = serializers.UserReceiveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            message = {'confirmation_code': 'Код подтверждения невалиден'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """ Вьюсет для обьектов модели User """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (IsSuperUserOrIsAdminOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username',)

    @action(detail=False,
            methods=['GET', 'PATCH', 'DELETE'],
            url_path=r'(?P<username>[\w.@+-]+)',
            url_name='get_user')
    def user_by_username(self, request, username=None):
        """ Позволяет получить данные о пользователе, изменить их, удалить пользователя
        для администраторов и суперпользователей """
        user = get_object_or_404(User.objects.all(), username=username)
        if self.request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif self.request.method == 'PATCH':
            serializer = serializers.UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False,
            methods=['GET', 'PATCH'],
            permission_classes=(IsAuthenticated, ),
            url_path=r'me',
            url_name='me')
    def user_by_me(self, request):
        """ Позволяет авторизованному пользователю получить данные о себе и изменит их """
        user = self.request.user
        if self.request.method == 'PATCH':
            serializer = serializers.UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(CreateListDestroyViewSet):
    """ Вьюсет для объекто модели Category """
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    """ Вьюсет для объекта модели Genre """
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """ Вьюсет для объекта модели Title """
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = serializers.TitleSerializer
    permission_classes = (AnonimReadOnly | IsSuperUserOrIsAdminOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """ Определяет нужный сериализатор """
        if self.request.method == 'GET':
            return serializers.TitleGETSerializer
        return serializers.TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = (IsAuthorOrIsModeratorOrIsAdminOrIsSuperUserOnly,)
    pagination_class = PageNumberPagination

    def get_title(self):
        """ Возвращает объект текущего произведения """
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        """ Возвращает queryset c отзывами для текущего произведения """
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """ """
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    permission_classes = (IsAuthorOrIsModeratorOrIsAdminOrIsSuperUserOnly,)
    pagination_class = PageNumberPagination

    def get_review(self):
        """ Возвращает объект текущего обзора """
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        """ Возвращает queryset c комментариями для текущего комментария """
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """ Создает комментарий для текущего отзыва,
        где автором является текущий пользователь """
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
