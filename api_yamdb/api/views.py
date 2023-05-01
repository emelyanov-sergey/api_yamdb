from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title, User
from api.filters import TitleFilterByNameCategoryGenreYear
from api.permissions import (IsAdmin, IsAdminOrReadOnly,
                             IsModeratorAdminOwnerOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             ConfirmationSerializer, GenreSerializer,
                             ReadOnlyTitleSerializer, ReviewSerializer,
                             TitleSerializer, TokenSerializer, UserSerializer)
from api.mixins import CreateDeleteListViewSet


class ConfirmationView(APIView):
    """Отправка confirmation_code на email, введенный при регистрации."""
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = ConfirmationSerializer

    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        if User.objects.filter(username=username, email=email).exists():
            return Response(serializer.data, status=status.HTTP_200_OK)
        user, create = User.objects.get_or_create(
            username=username,
            email=email
        )
        code = default_token_generator.make_token(user)
        user.confirmation_code = code
        user.save()
        send_mail(
            'Код получения токена',
            f'Ваш код: {code}',
            'user@ya.ru',
            [user.email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    """Отправка токена при получении confirmation_code и username."""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.validated_data['confirmation_code']
        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response({'confirmation_code': 'no!'},
                        status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAdmin,)
    pagination_class = LimitOffsetPagination

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=UserSerializer,
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(CreateDeleteListViewSet):
    """Вьюсет для модели Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (SearchFilter,)
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateDeleteListViewSet):
    """Вьюсет для модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Title."""
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilterByNameCategoryGenreYear
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadOnlyTitleSerializer
        return TitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Comment."""
    serializer_class = CommentSerializer
    permission_classes = (IsModeratorAdminOwnerOrReadOnly,)

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
    """Вьюсет для модели Review."""
    serializer_class = ReviewSerializer
    permission_classes = (IsModeratorAdminOwnerOrReadOnly,)

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
