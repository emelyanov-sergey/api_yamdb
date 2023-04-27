from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter

from reviews.models import User, Category, Genre, Title, Review, Comment
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleSerializer, ReadOnlyTitleSerializer,
                          CommentSerializer, UserSerializer,
                          GetTokenSerializer, AdminSerializer,
                          SignUpSerializer)
from .mixins import CreateDeleteListViewSet
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorOrModeratorOrReadOnly)


class UserCreation(APIView):
    """Вьюсет создания юзера и отправки сообщения на почту"""

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['mail_subject'],
            body=data['email_info'],
            from_email=settings.EMAIL_ADMIN,
            to=[data['to_email']],
        )
        email.send()

    @staticmethod
    def token_generator(user):
        return default_token_generator.make_token(user)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user, created = User.objects.get_or_create(
            username=data.get('username'),
            email=data.get('email')
        )
        user.confirmation_code = self.token_generator(user)
        data = {
            'subject': f'Код подтверждения для {user.username}',
            'message': user.confirmation_code,
            'to_email': user.email
        }
        self.send_email(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class JWTTokenConfirmation(APIView):
    """Создание JWT токена через код пользователя"""

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        current_user = get_object_or_404(
            User, username=data.get('username'),
        )
        if data['confirmation_code'] == current_user.confirmation_code:
            refreshed_token = RefreshToken.for_user(current_user)
            return Response({
                'JWT-Код': str(refreshed_token.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет Users."""

    queryset = User.objects.all()
    serializer_class = AdminSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthenticated, IsAdmin)
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        url_path='me',
        methods=['GET', 'PATCH'],
        permission_classes=(IsAuthenticated,)
    )
    def get_or_patch_self_profile(self, request):
        """Пользователь может изменить и получить данные о себе."""
        user = get_object_or_404(User, id=request.user.id)
        if request.method == 'GET':
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(CreateDeleteListViewSet):
    """Вьюсет для категорий. Сразу добавил поиск"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ["name"]
    lookup_field = "slug"


class GenreViewSet(CreateDeleteListViewSet):
    """Вьюсет для жанров. так же как и выше добавил домашку."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    search_fields = ["name"]
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений. К каждому сразу добавил среднюю оценку."""

    queryset = Title.objects.all().annotate(
        Avg("reviews__score")
    ).order_by("name")
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return ReadOnlyTitleSerializer
        return TitleSerializer

class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Comment."""

    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_review(self):
        """Возвращает объект текущего отзыва."""
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        """Возвращает комментарии для текущего отзыва."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Создает комментарий для текущего отзыва,
        где автор это текущий пользователь."""
        serializer.save(author=self.request.user, review=self.get_review())


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов модели Review."""

    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get_title(self):
        """Возвращает объект текущего произведения."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Возвращает queryset c отзывами для текущего произведения."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Создает отзыв для текущего произведения,
        где автор это текущий пользователь."""
        serializer.save(author=self.request.user, title=self.get_title())
