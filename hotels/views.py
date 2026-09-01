from rest_framework import viewsets
from .models import Hotel, Room, Guest, Booking
from .serializers import HotelSerializer, RoomSerializer, GuestSerializer, BookingSerializer, RegisterSerializer, MeSerializer
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from .permissions import IsStaffOrReadOnly, IsOwnerOrStaff, IsHotelOwnerOrReadOnly
from .filters import RoomFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample


@extend_schema_view(
    list=extend_schema(
        summary='List hotels',
        description='Guests and anonymous users see all hotels. '
                    'A manager sees only the hotels they own.',
    ),
    retrieve=extend_schema(
        summary='Retrieve a hotel',
        responses={200: HotelSerializer, 404: None},
    ),
    create=extend_schema(
        summary='Create a hotel',
        description='Staff only. The authenticated user becomes the owner.',
        responses={201: HotelSerializer, 403: None},
    ),
    update=extend_schema(
        summary='Update a hotel',
        responses={200: HotelSerializer, 404: None},
    ),
    partial_update=extend_schema(
        summary='Partially update a hotel',
        responses={200: HotelSerializer, 404: None},
    ),
    destroy=extend_schema(
        summary='Delete a hotel',
        responses={204: None, 404: None},
    ),
)
class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsHotelOwnerOrReadOnly]
    filterset_fields = ['city']
    search_fields = ['name', 'city']
    ordering_fields = ['name', 'city']


    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated or user.is_superuser:
            return Hotel.objects.all()
        if user.is_staff:
            return Hotel.objects.filter(owner=user)
        return Hotel.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

@extend_schema_view(
    list=extend_schema(
        summary='List rooms',
        description='Pass check_in and check_out to get only rooms that are free for those dates. '
                    'A manager sees only rooms in their own hotels.',
        parameters=[
            OpenApiParameter('check_in', str, description='Check-in date, YYYY-MM-DD'),
            OpenApiParameter('check_out', str, description='Check-out date, YYYY-MM-DD'),
        ],
    ),
    retrieve=extend_schema(
        summary='Retrieve a room',
        responses={200: RoomSerializer, 404: None},
    ),
    create=extend_schema(
        summary='Create a room',
        description='Staff only. The room must belong to a hotel owned by the current user.',
        responses={201: RoomSerializer, 400: None, 403: None},
    ),
    update=extend_schema(
        summary='Update a room',
        responses={200: RoomSerializer, 404: None},
    ),
    partial_update=extend_schema(
        summary='Partially update a room',
        responses={200: RoomSerializer, 404: None},
    ),
    destroy=extend_schema(
        summary='Delete a room',
        responses={204: None, 404: None},
    ),
)
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsHotelOwnerOrReadOnly]
    filterset_class = RoomFilter
    ordering_fields = ['price_per_night', 'number']


    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.is_staff and not user.is_superuser:
            queryset = Room.objects.filter(hotel__owner=user)
        else:
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


@extend_schema_view(
    list=extend_schema(
        summary='List guests',
        description='Staff only. A manager sees only guests who booked in their hotels.',
    ),
    retrieve=extend_schema(summary='Retrieve a guest', responses={200: GuestSerializer, 404: None}),
    create=extend_schema(summary='Create a guest'),
    update=extend_schema(summary='Update a guest'),
    partial_update=extend_schema(summary='Partially update a guest'),
    destroy=extend_schema(summary='Delete a guest'),
)
class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Guest.objects.all()
        return Guest.objects.filter(booking__room__hotel__owner=user).distinct()
    

@extend_schema_view(
    list=extend_schema(
        summary='List bookings',
        description='A guest sees their own bookings, a manager sees bookings for rooms '
                    'in their hotels, an administrator sees all bookings.',
    ),
    retrieve=extend_schema(
        summary='Retrieve a booking',
        responses={200: BookingSerializer, 404: None},
    ),
    create=extend_schema(
        summary='Create a booking',
        description='Send only room_id and dates. The guest is taken from the token. '
                    'Returns 409 if the room is already booked for the selected dates.',
        responses={201: BookingSerializer, 400: None, 401: None, 409: None},
        examples=[
            OpenApiExample(
                'Booking request',
                value={'room_id': 1, 'check_in': '2027-07-01', 'check_out': '2027-07-05'},
                request_only=True,
            ),
        ],
    ),
    update=extend_schema(
        summary='Update a booking',
        responses={200: BookingSerializer, 400: None, 404: None},
    ),
    partial_update=extend_schema(
        summary='Partially update a booking',
        description='Status transitions are restricted: pending to confirmed or cancelled, '
                    'confirmed to completed or cancelled. Completed and cancelled are final.',
        responses={200: BookingSerializer, 400: None, 404: None},
        examples=[
            OpenApiExample(
                'Confirm a booking',
                value={'status': 'confirmed'},
                request_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        summary='Delete a booking',
        responses={204: None, 404: None},
    ),
)
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]
    filterset_fields = ['status', 'room']
    ordering_fields = ['check_in', 'check_out']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Booking.objects.all()
        if user.is_staff:
            return Booking.objects.filter(room__hotel__owner=user)
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


@extend_schema(
    summary='Register a new user',
    description='Set role to guest or owner. An owner gets staff access and can manage hotels.',
    responses={201: None, 400: None},
    examples=[
        OpenApiExample(
            'Register as a guest',
            value={
                'username': 'john',
                'password': 'strongpass123',
                'email': 'john@example.com',
                'full_name': 'John Doe',
                'phone': '+380501112233',
                'role': 'guest',
            },
            request_only=True,
        ),
    ],
)
class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

@extend_schema_view(
    get=extend_schema(summary='Retrieve my profile'),
    put=extend_schema(summary='Update my profile'),
    patch=extend_schema(summary='Partially update my profile'),
)
class MeView(RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.guest_profile