from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (CategoryViewSet, GenreViewSet,
                       TitleViewSet, UserViewSet, UserCreation,
                       JWTTokenConfirmation, CommentViewSet, ReviewViewSet)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'categories', CategoryViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'comments', CommentViewSet)
router_v1.register(r'comments', ReviewViewSet)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', UserCreation.as_view(), name='signup'),
    path('v1/auth/token/', JWTTokenConfirmation.as_view(), name='token'),
]
