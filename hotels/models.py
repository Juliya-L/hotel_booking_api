from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.name


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

    
    def __str__(self):
        return f'{self.hotel} - Room {self.number}'
    

class Guest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='guest_profile', null=True, blank=True)
    full_name = models.CharField(max_length=30)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.full_name} - Phone {self.phone}'


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
    price_at_booking = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(check_out__gt=models.F('check_in')),
                name='check_out_after_check_in',
            )
        ]

    def clean(self):
        if self.check_in and self.check_out:
            if self.check_out <= self.check_in:
                raise ValidationError('Check-out date must be later than check-in date.')

            if self.status != 'cancelled':
                conflicting = Booking.objects.filter(
                    room=self.room,
                    check_in__lt=self.check_out,
                    check_out__gt=self.check_in,
                ).exclude(status='cancelled').exclude(pk=self.pk)

                if conflicting.exists():
                    raise ValidationError('This room is already booked for the selected dates.')

    def save(self, *args, **kwargs):
        if self.price_at_booking is None and self.room_id:
            self.price_at_booking = self.room.price_per_night
        super().save(*args, **kwargs)
        

    def __str__(self):
        return f'{self.guest} - {self.room} - {self.check_in} - {self.check_out} - {self.status}'

