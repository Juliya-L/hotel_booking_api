from django.contrib import admin
from .models import Hotel, Room, Guest, Booking

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
  list_display = ['name', 'city']
  search_fields = ['name', 'city']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
  list_display = ['hotel', 'number', 'room_type', 'price_per_night' ]
  list_filter = ['room_type']
  search_fields = ['number']


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
  list_display = ['full_name', 'email', 'phone']
  search_fields = ['phone']
  

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
  list_display = ['guest', 'room', 'check_in', 'check_out']
  list_filter = ['status']


