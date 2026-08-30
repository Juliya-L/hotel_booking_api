import pytest
from datetime import date
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from hotels.models import Hotel, Room, Guest, Booking


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def room(db):
    owner = User.objects.create_user(username='owner_p', password='pass12345', is_staff=True)
    hotel = Hotel.objects.create(owner=owner, name='Hotel P', city='Kyiv')
    return Room.objects.create(hotel=hotel, number='101', price_per_night=1500)


@pytest.mark.django_db
def test_price_is_frozen_at_booking(room):
    guest = Guest.objects.create(full_name='Kate', email='k@e.com', phone='+380504444444')

    booking = Booking.objects.create(
        room=room, guest=guest,
        check_in=date(2027, 9, 1), check_out=date(2027, 9, 4),
    )

    assert booking.price_at_booking == 1500

    room.price_per_night = 9000
    room.save()
    booking.refresh_from_db()

    assert booking.price_at_booking == 1500


@pytest.mark.django_db
def test_total_price_uses_frozen_price(room):
    from hotels.serializers import BookingSerializer

    guest = Guest.objects.create(full_name='Kate', email='k@e.com', phone='+380504444444')
    booking = Booking.objects.create(
        room=room, guest=guest,
        check_in=date(2027, 9, 1), check_out=date(2027, 9, 4),
    )

    room.price_per_night = 9000
    room.save()
    booking.refresh_from_db()

    data = BookingSerializer(booking).data

    assert data['nights'] == 3
    assert data['total_price'] == '4500.00'


@pytest.mark.django_db
def test_register_as_owner_sets_staff(api_client):
    response = api_client.post('/api/register/', {
        'username': 'new_owner',
        'password': 'pass12345',
        'email': 'o@e.com',
        'full_name': 'New Owner',
        'phone': '+380505555555',
        'role': 'owner',
    }, format='json')

    assert response.status_code == 201
    assert response.data['role'] == 'owner'

    user = User.objects.get(username='new_owner')
    assert user.is_staff is True


@pytest.mark.django_db
def test_register_as_guest_is_not_staff(api_client):
    response = api_client.post('/api/register/', {
        'username': 'new_guest',
        'password': 'pass12345',
        'email': 'g@e.com',
        'full_name': 'New Guest',
        'phone': '+380506666666',
        'role': 'guest',
    }, format='json')

    assert response.status_code == 201

    user = User.objects.get(username='new_guest')
    assert user.is_staff is False
    assert user.guest_profile.full_name == 'New Guest'