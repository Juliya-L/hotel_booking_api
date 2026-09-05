# Hotel Booking API

A REST API for a hotel booking platform, built with Django and Django REST Framework.

The platform supports two roles: guests who book rooms, and hotel owners who manage their
own hotels and rooms. Data is isolated per owner — a manager only sees their own hotels,
rooms and the bookings made in them.

## Live demo

- API documentation — https://web-production-3642a.up.railway.app/api/docs/ 


## Tech stack

- Python 3.12, Django 6.0, Django REST Framework
- JWT authentication (`djangorestframework-simplejwt`)
- PostgreSQL in production, SQLite for local development
- OpenAPI schema and Swagger UI (`drf-spectacular`)
- Filtering with `django-filter`
- Tests with `pytest` and `pytest-django`

## Features

**Booking logic**
- Date overlap detection — a room cannot be double booked
- Protection against race conditions using `transaction.atomic` and `select_for_update`
- Check-in cannot be in the past, check-out must be after check-in
- Room price is frozen at booking time, so later price changes do not affect existing bookings
- Status transitions are restricted: `pending → confirmed → completed`, with `cancelled`
  reachable from the first two. `completed` and `cancelled` are final

**Access control**
- JWT authentication with access and refresh tokens
- Registration as a guest or as a hotel owner
- Query scoping — each role sees only the data it is allowed to see
- Object-level permissions — a manager cannot access another owner's hotel even by id

**Data integrity**
- Validation on three levels: serializer, model `clean()`, and database constraints
- Database-level checks for `check_out > check_in` and positive room price

**API quality**
- Pagination, filtering, search and ordering on list endpoints
- Rooms can be filtered by availability for a date range, by city, hotel name and price range
- Full OpenAPI documentation with request examples

## Local setup

```bash
git clone https://github.com/Juliya-L/hotel_booking_api.git
cd hotel_booking_api

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

Create a `.env` file in the project root, using `.env.example` as a template:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

Generate a secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Apply migrations and start the server:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API documentation

With the server running, open:

- Swagger UI — http://127.0.0.1:8000/api/docs/
- OpenAPI schema — http://127.0.0.1:8000/api/schema/
- Django admin — http://127.0.0.1:8000/admin/

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register/` | Register as a guest or hotel owner |
| POST | `/api/token/` | Obtain access and refresh tokens |
| POST | `/api/token/refresh/` | Refresh an access token |
| GET, PATCH | `/api/me/` | Current user's profile |
| GET, POST | `/api/hotels/` | List or create hotels |
| GET, PUT, PATCH, DELETE | `/api/hotels/{id}/` | Retrieve, update or delete a hotel |
| GET, POST | `/api/rooms/` | List or create rooms |
| GET, PUT, PATCH, DELETE | `/api/rooms/{id}/` | Retrieve, update or delete a room |
| GET, POST | `/api/bookings/` | List or create bookings |
| GET, PUT, PATCH, DELETE | `/api/bookings/{id}/` | Retrieve, update or delete a booking |
| GET | `/api/guests/` | List guests (staff only) |

### Example: find available rooms

```
GET /api/rooms/?city=Kyiv&check_in=2027-07-01&check_out=2027-07-05&ordering=price_per_night
```

### Example: create a booking

```json
POST /api/bookings/
{
  "room_id": 1,
  "check_in": "2027-07-01",
  "check_out": "2027-07-05"
}
```

The guest is taken from the authentication token, not from the request body.

## Tests

```bash
python -m pytest
```

The suite covers date conflicts, status transitions, access control for guests and
managers, price freezing and registration roles.