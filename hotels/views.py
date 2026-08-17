from rest_framework import viewsets
from .models import Hotel, Room, Guest, Booking
from .serializers import HotelSerializer, RoomSerializer, GuestSerializer, BookingSerializer


class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


    def get_queryset(self):
        queryset = Room.objects.all()

        check_in = self.request.query_params.get('check_in')
        check_out = self.request.query_params.get('check_out')

        if check_in and check_out:
            booked_room_ids = Booking.objects.filter(
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).exclude(status='cancelled').values_list('room_id', flat=True)

            queryset = queryset.exclude(id__in=booked_room_ids)

        return queryset



class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer