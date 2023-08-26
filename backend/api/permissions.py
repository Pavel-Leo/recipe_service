from rest_framework import permissions
from rest_framework.request import Request


class IsAdminOwnerOrReadOnly(permissions.BasePermission):
    """Кастомный класс для проверки прав доступа.
    Проверяет имеет ли пользователь права администратора для запроса, либо
    является автором.
    """

    def has_permission(
        self: any,
        request: Request,
        view: any,
    ) -> bool:
        return request.method in permissions.SAFE_METHODS or (
            request.user and request.user.is_authenticated
        )

    def has_object_permission(
        self: any,
        request: Request,
        view: any,
        obj: any,
    ) -> bool:
        return (request.method in permissions.SAFE_METHODS
                or (request.user and request.user.is_authenticated
                    and (obj.author == request.user or request.user.is_staff))
                )
