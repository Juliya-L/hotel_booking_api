import pytest
from datetime import date
from django.contrib.auth.models import User
from hotels.models import Hotel, Room, Guest, Booking
from hotels.serializers import BookingSerializer


@pytest.fixture
def booking(db):
    owner = User.objects.create_user(username='owner_s', password='pass12345', is_staff=True)
    hotel = Hotel.objects.create(owner=owner, name='Hotel S', city='Kyiv')
    room = Room.objects.create(hotel=hotel, number='101', price_per_night=1000)
    guest = Guest.objects.create(full_name='Sam', email='s@e.com', phone='+380503333333')
    return Booking.objects.create(
        room=room, guest=guest,
        check_in=date(2027, 8, 1), check_out=date(2027, 8, 3),
    )


@pytest.mark.django_db
def test_pending_can_become_confirmed(booking):
    serializer = BookingSerializer(booking, data={'status': 'confirmed'}, partial=True)

    assert serializer.is_valid() is True


@pytest.mark.django_db
def test_cancelled_cannot_become_confirmed(booking):
    booking.status = 'cancelled'
    booking.save()

    serializer = BookingSerializer(booking, data={'status': 'confirmed'}, partial=True)

    assert serializer.is_valid() is False
    assert 'status' in serializer.errors


@pytest.mark.django_db
def test_completed_is_final(booking):
    booking.status = 'completed'
    booking.save()

    serializer = BookingSerializer(booking, data={'status': 'pending'}, partial=True)

    assert serializer.is_valid() is False