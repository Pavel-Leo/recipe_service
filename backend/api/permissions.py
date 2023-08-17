from django.http import HttpRequest
from rest_framework import permissions

class IsAdminOwnerOrReadOnly(permissions.BasePermission):
    """Кастомный класс для проверки прав доступа.
    Проверяет, имеет ли пользователь права администратора для запроса, либо
    является автором.
    """

    def has_object_permission(
        self: any,
        request: HttpRequest,
        view: any,
        obj: any,
    ) -> bool:
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or (request.user == obj.author)
        )
