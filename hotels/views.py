from rest_framework import viewsets
from .models import Hotel, Room, Guest, Booking
from .serializers import HotelSerializer, RoomSerializer, GuestSerializer, BookingSerializer, RegisterSerializer
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView
from .permissions import IsStaffOrReadOnly, IsOwnerOrStaff



class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsStaffOrReadOnly]


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsStaffOrReadOnly]


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
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(guest__user=user)
    


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            guest = request.user.guest_profile
        except Guest.DoesNotExist:
            return Response(
                {'detail': 'Your account has no guest profile.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

            serializer.save(guest=guest)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]