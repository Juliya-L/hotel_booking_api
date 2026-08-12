from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, RoomViewSet, GuestViewSet, BookingViewSet

router = DefaultRouter()
router.register(r'hotels', HotelViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'guests', GuestViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

