from rest_framework import serializers
from .models import Hotel, Room, Guest, Booking
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction

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
        fields = ['id', 'room', 'guest', 'room_id', 'check_in', 'check_out', 'nights', 'price_at_booking', 'total_price', 'status']
        read_only_fields = ['price_at_booking']



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
        today = timezone.now().date()

        if data['check_in'] < today:
            raise serializers.ValidationError('Check-in date cannot be in the past.')
        
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


    def get_total_price(self, obj):
        price = obj.price_at_booking or obj.room.price_per_night
        return str(price * self.get_nights(obj))



class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=30)
    phone = serializers.CharField(max_length=20)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password'],
                email=validated_data['email'],
            )
            guest = Guest.objects.create(
                user=user,
                full_name=validated_data['full_name'],
                email=validated_data['email'],
                phone=validated_data['phone'],
            )
        return guest

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'username': instance.user.username,
            'email': instance.user.email,
            'full_name': instance.full_name,
            'phone': instance.phone,
        }