import pytest
from datetime import date
from django.contrib.auth.models import User
from hotels.models import Hotel, Room, Guest, Booking


@pytest.fixture
def room():
    owner = User.objects.create_user(username='owner_test', password='pass12345')
    hotel = Hotel.objects.create(owner=owner, name='Test Hotel', city='Kyiv')
    return Room.objects.create(hotel=hotel, number='101', price_per_night=1000)


@pytest.fixture
def guest():
    user = User.objects.create_user(username='guest_test', password='pass12345')
    return Guest.objects.create(user=user, full_name='John Doe', email='j@e.com', phone='+380501112233')


@pytest.mark.django_db
def test_overlapping_booking_is_rejected(room, guest):
    Booking.objects.create(
        room=room,
        guest=guest,
        check_in=date(2027, 3, 1),
        check_out=date(2027, 3, 5),
    )

    from hotels.serializers import BookingSerializer

    serializer = BookingSerializer(data={
        'room_id': room.id,
        'check_in': '2027-03-03',
        'check_out': '2027-03-07',
    })

    assert serializer.is_valid() is False
    assert 'already booked' in str(serializer.errors)


@pytest.mark.django_db
def test_non_overlapping_booking_is_allowed(room, guest):
    Booking.objects.create(
        room=room,
        guest=guest,
        check_in=date(2027, 3, 1),
        check_out=date(2027, 3, 5),
    )

    from hotels.serializers import BookingSerializer

    serializer = BookingSerializer(data={
        'room_id': room.id,
        'check_in': '2027-03-05',
        'check_out': '2027-03-08',
    })

    assert serializer.is_valid() is True