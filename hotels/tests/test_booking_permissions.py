import pytest
from datetime import date
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from hotels.models import Hotel, Room, Guest, Booking


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def hotel_with_room(db):
    owner = User.objects.create_user(username='owner_x', password='pass12345', is_staff=True)
    hotel = Hotel.objects.create(owner=owner, name='Hotel X', city='Kyiv')
    room = Room.objects.create(hotel=hotel, number='101', price_per_night=1000)
    return room


@pytest.fixture
def guest_alice(db):
    user = User.objects.create_user(username='alice', password='pass12345')
    profile = Guest.objects.create(user=user, full_name='Alice', email='a@e.com', phone='+380501111111')
    return {'user': user, 'profile': profile}


@pytest.fixture
def guest_bob(db):
    user = User.objects.create_user(username='bob', password='pass12345')
    profile = Guest.objects.create(user=user, full_name='Bob', email='b@e.com', phone='+380502222222')
    return {'user': user, 'profile': profile}


@pytest.mark.django_db
def test_guest_sees_only_own_bookings(api_client, hotel_with_room, guest_alice, guest_bob):
    Booking.objects.create(
        room=hotel_with_room, guest=guest_alice['profile'],
        check_in=date(2027, 5, 1), check_out=date(2027, 5, 3),
    )
    Booking.objects.create(
        room=hotel_with_room, guest=guest_bob['profile'],
        check_in=date(2027, 6, 1), check_out=date(2027, 6, 3),
    )

    api_client.force_authenticate(user=guest_alice['user'])
    response = api_client.get('/api/bookings/')

    assert response.status_code == 200
    assert response.data['count'] == 1
    assert response.data['results'][0]['guest']['full_name'] == 'Alice'


@pytest.mark.django_db
def test_guest_cannot_access_foreign_booking(api_client, hotel_with_room, guest_alice, guest_bob):
    bob_booking = Booking.objects.create(
        room=hotel_with_room, guest=guest_bob['profile'],
        check_in=date(2027, 6, 1), check_out=date(2027, 6, 3),
    )

    api_client.force_authenticate(user=guest_alice['user'])
    response = api_client.get(f'/api/bookings/{bob_booking.id}/')

    assert response.status_code == 404


@pytest.mark.django_db
def test_booking_guest_taken_from_token(api_client, hotel_with_room, guest_alice):
    api_client.force_authenticate(user=guest_alice['user'])

    response = api_client.post('/api/bookings/', {
        'room_id': hotel_with_room.id,
        'check_in': '2027-07-01',
        'check_out': '2027-07-03',
    }, format='json')

    assert response.status_code == 201
    assert response.data['guest']['full_name'] == 'Alice'

    booking = Booking.objects.get(id=response.data['id'])
    assert booking.guest == guest_alice['profile']


@pytest.mark.django_db
def test_anonymous_cannot_create_booking(api_client, hotel_with_room):
    response = api_client.post('/api/bookings/', {
        'room_id': hotel_with_room.id,
        'check_in': '2027-07-01',
        'check_out': '2027-07-03',
    }, format='json')

    assert response.status_code == 401