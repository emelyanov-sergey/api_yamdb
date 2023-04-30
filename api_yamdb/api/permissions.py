from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Проверка на права доступа для Админа или только для чтения."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (request.user.is_authenticated
                and request.user.role == 'admin')

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == 'admin'


class IsAdmin(BasePermission):
    """Проверка на права доступа для Админа."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_admin
                or request.user.is_superuser)


class IsAuthorOrModeratorOrReadOnly(BasePermission):
    """Проверка на права доступа для Модератора или Автора."""

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, "role"):
            return (
                view.action in self.safe_actions
                or request.user.role == 'moderator'
                or request.user.role == 'admin'
                or request.user == obj.author
            )
        return view.action in self.safe_actions


class IsModeratorAdminOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.role == 'admin'
                or request.user.role == 'moderator'
                or obj.author == request.user)

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)
