from rest_framework import filters, viewsets, status
from reviews.models import User, Category, Genre, Title, Review, Comment
from .permissions import (IsAdminOrReadOnly,)
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleSerializer, ReadOnlyTitleSerializer,
                          CommentSerializer, UserSerializer,
                          GetTokenSerializer)
from .mixins import CreateDeleteListViewSet
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import viewsets, filters, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
)
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User
from .permissions import IsAdminOnly, ReadOnly, IsAuthorOrModeratorOrReadOnly
from .serializers import UserSerializer


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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAdminOnly,)
    serializer_class = UserSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'head', 'patch', 'delete')

    @action(
        detail=False,
        methods=('GET', 'PATCH'),
        url_path='me',
        permission_classes=(IsAuthenticated,),
        serializer_class=UserSerializer
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


def send_email(data):
    email = EmailMessage(
        subject=data['mail_subject'],
        body=data['email_info'],
        from_email=settings.EMAIL_ADMIN,
        to=[data['to_email']]
    )
    email.send()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user, created = User.objects.get_or_create(
        username=serializer.validated_data['username'],
        email=serializer.validated_data['email']
    )
    confirmation_code = default_token_generator.make_token(user)
    email_text = f'Confirmation code {confirmation_code}'
    data = {
        'email_info': email_text,
        'to_email': user.email,
        'mail_subject': 'Confirmation code'
    }
    send_email(data)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )

    if user.confirmation_code == serializer.validated_data.get(
            'confirmation_code'
    ):
        token = RefreshToken.for_user(user).access_token
        return Response({'token': str(token)}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
