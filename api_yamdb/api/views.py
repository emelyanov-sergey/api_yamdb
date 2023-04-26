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
