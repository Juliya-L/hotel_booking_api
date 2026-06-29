from rest_framework import serializers
from .models import Hotel, Room, Guest, Booking

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
    
    class Meta:
        model = Booking
        fields = ['id', 'room', 'guest', 'room_id', 'guest_id', 'check_in', 'check_out', 'status']


