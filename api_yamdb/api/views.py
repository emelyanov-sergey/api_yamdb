from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from reviews.models import User
from .permissions import IsAdminOnly
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAdminOnly,)
    serializer_class = UserSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'head', 'patch', 'delete')
