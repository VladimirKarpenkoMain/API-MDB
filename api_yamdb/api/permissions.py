from rest_framework import permissions


class IsSuperUserOrIsAdminOnly(permissions.BasePermission):
    """ Разрешает запросы только администратарам и суперпользователям """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
                request.user.is_admin or request.user.is_superuser or request.user.is_staff)


class AnonimReadOnly(permissions.BasePermission):
    """ Разрешает анонимному пользователю только безопасные запросы """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthorOrIsModeratorOrIsAdminOrIsSuperUserOnly(permissions.BasePermission):
    """ Разрешает анонимному пользователю только безопасные запросы, а действия с объектом только
     авторам, модераторам, администраторам и суперпользователям """
    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user or request.user.is_admin or request.user.is_moderator
                or request.user.is_staff or request.user.is_superuser)
