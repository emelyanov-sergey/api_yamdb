from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Проверка на права доступа для Админа или только для чтения."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin)


class IsAdmin(BasePermission):
    """Проверка на права доступа для Админа."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_admin)


class IsModeratorAdminOwnerOrReadOnly(BasePermission):
    """Проверка на права доступа - является ли юзер модератором,
    админом или автором, или только чтение."""

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user)

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)
