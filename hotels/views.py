from rest_framework import viewsets
from .models import Hotel, Room, Guest, Booking
from .serializers import HotelSerializer, RoomSerializer, GuestSerializer, BookingSerializer, RegisterSerializer
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            room = serializer.validated_data['room']
            Room.objects.select_for_update().get(pk=room.pk)

            conflicting = Booking.objects.filter(
                room=room,
                check_in__lt=serializer.validated_data['check_out'],
                check_out__gt=serializer.validated_data['check_in'],
            ).exclude(status='cancelled')

            if conflicting.exists():
                return Response(
                    {'non_field_errors': ['This room is already booked for the selected dates.']},
                    status=status.HTTP_409_CONFLICT,
                )

            serializer.save()

        return Response(serializer.data, status=satatus.HTTP_201_CREATED)

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]