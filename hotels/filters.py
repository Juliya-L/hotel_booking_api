import django_filters
from .models import Room, Booking


class RoomFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(field_name='hotel__city', lookup_expr='iexact')
    hotel_name = django_filters.CharFilter(field_name='hotel__name', lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='lte')

    class Meta:
        model = Room
        fields = ['hotel', 'room_type', 'city', 'hotel_name', 'min_price', 'max_price']
        