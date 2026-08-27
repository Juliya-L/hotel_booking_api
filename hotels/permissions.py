from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Hotel


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff



class IsOwnerOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.is_staff:
            return obj.room.hotel.owner == request.user
        return obj.guest.user == request.user


class IsHotelOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        hotel = obj if isinstance(obj, Hotel) else obj.hotel
        return hotel.owner == request.user