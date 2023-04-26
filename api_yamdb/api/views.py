<<<<<<< HEAD
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, filters, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
)

from reviews.models import User
from .permissions import IsAdminOnly, ReadOnly, IsAuthorOrModeratorOrReadOnly
from .serializers import UserSerializer


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
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)
=======
from rest_framework import filters, viewsets
from reviews.models import User, Category, Genre, Title, Review, Comment
from .permissions import (IsAdminOrReadOnly,)
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleSerializer, ReadOnlyTitleSerializer,
                          CommentSerializer, UserSerializer)
from .mixins import CreateDeleteListViewSet
from django.db.models import Avg


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
>>>>>>> d30f9104da220ed769aa69bd5aacba9cba983031
