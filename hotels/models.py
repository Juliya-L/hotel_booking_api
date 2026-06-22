from django.db import models

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)


class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ("single", "Single Room"),
        ("standard", "Standard Room"),
        ("family", "Family Room"),
        ("suite", "Suite"),
        ("presidential", "Presidential Suite"),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT)
    number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=30, choices=ROOM_TYPE_CHOICES, default='standard')
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    

class Guest(models.Model):
    full_name = models.CharField(max_length=30)
    email = models.EmailField()
    phone = models.CharField(max_length=20)


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    guest = models.ForeignKey(Guest, on_delete=models.PROTECT)
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')


