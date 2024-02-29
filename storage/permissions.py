from rest_framework import exceptions
from rest_framework.permissions import BasePermission

from storage.models import File, Access


class IsOwnerPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        file_id = view.kwargs['file_id']

        if file_id:
            file = File.objects.filter(file_id=file_id).first()
            if file is None:
                raise exceptions.NotFound()
            if Access.objects.filter(user=request.user, file=file, isOwner=True).exists():
                return True

        return False

class IsAccessPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        file_id = view.kwargs['file_id']

        if file_id:
            file = File.objects.filter(file_id=file_id).first()
            if file is None:
                raise exceptions.NotFound()

            if Access.objects.filter(user=request.user, file=file).exists():
                return True

        return False
