import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from hotels.models import Hotel, Room, Guest, Booking
from datetime import date


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def manager_a(db):
    user = User.objects.create_user(username='manager_a', password='pass12345', is_staff=True)
    hotel = Hotel.objects.create(owner=user, name='Hotel A', city='Kyiv')
    return {'user': user, 'hotel': hotel}


@pytest.fixture
def manager_b(db):
    user = User.objects.create_user(username='manager_b', password='pass12345', is_staff=True)
    hotel = Hotel.objects.create(owner=user, name='Hotel B', city='Lviv')
    return {'user': user, 'hotel': hotel}


@pytest.mark.django_db
def test_manager_sees_only_own_hotels(api_client, manager_a, manager_b):
    api_client.force_authenticate(user=manager_a['user'])

    response = api_client.get('/api/hotels/')

    assert response.status_code == 200
    assert response.data['count'] == 1
    assert response.data['results'][0]['name'] == 'Hotel A'


@pytest.mark.django_db
def test_manager_cannot_edit_foreign_hotel(api_client, manager_a, manager_b):
    api_client.force_authenticate(user=manager_a['user'])

    response = api_client.patch(
        f"/api/hotels/{manager_b['hotel'].id}/",
        {'name': 'Hacked'},
        format='json',
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_anonymous_sees_all_hotels(api_client, manager_a, manager_b):
    response = api_client.get('/api/hotels/')

    assert response.status_code == 200
    assert response.data['count'] == 2