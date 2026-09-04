from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Moderators").exists()


class IsOwnerOrModerator(BasePermission):

    def has_permission(self, request, view):
        if request.user.groups.filter(name='Moderators').exists():
            return True

        return request.user == view.get_object().owner


class IsOwner(BasePermission):

    def has_permission(self, request, view):
        return request.user == view.get_object().owner


class IsNotModerator(BasePermission):

    def has_permission(self, request, view):
        if not request.user.groups.filter(name='Moderators').exists():
            return True

        return False
