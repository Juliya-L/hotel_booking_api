from rest_framework import serializers
from .models import Hotel, Room, Guest, Booking
from django.utils import timezone

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'city']
  

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'hotel', 'number', 'room_type', 'price_per_night']


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['id', 'full_name', 'email', 'phone']


class BookingSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    guest = GuestSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), source='room', write_only=True)
    guest_id = serializers.PrimaryKeyRelatedField(queryset=Guest.objects.all(), source='guest', write_only=True)
    nights = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    ALLOWED_TRANSITIONS = {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['completed', 'cancelled'],
        'completed': [],
        'cancelled': [],
    }

   
    class Meta:
        model = Booking
        fields = ['id', 'room', 'guest', 'room_id', 'guest_id', 'check_in', 'check_out', 'nights', 'total_price', 'status']



    def get_nights(self, obj):
        return (obj.check_out - obj.check_in).days


    def get_total_price(self, obj):
        return str(obj.room.price_per_night * self.get_nights(obj))



    def validate_status(self, value):
        if self.instance is None:
            return value

        current = self.instance.status
        if value == current:
            return value

        if value not in self.ALLOWED_TRANSITIONS[current]:
            raise serializers.ValidationError(
                f"Cannot change status from '{current}' to '{value}'."
            )
        return value

    

    def validate(self, data):
        if data['check_out'] <= data['check_in']:
            raise serializers.ValidationError('Check-out date must be later than check-in date.')

        conflicting_bookings = Booking.objects.filter(
            room=data['room'],
            check_in__lt=data['check_out'],
            check_out__gt=data['check_in'],
        ).exclude(status='cancelled')

        if conflicting_bookings.exists():
            raise serializers.ValidationError('This room is already booked for the selected dates.')

        return data




