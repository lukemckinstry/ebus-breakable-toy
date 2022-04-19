from rest_framework import serializers
from .models import Route, Agency

class RouteSerializer(serializers.ModelSerializer):

    agency_name = serializers.CharField(read_only=True, source="agency_id.agency_name")

    class Meta:
        model = Route 

        fields = ['route_id', 'agency_name', 'route_short_name', 'route_long_name',
            'route_desc', 'route_type', 'route_url', 'route_color', 'route_distance',
            'trips_monday', 'trips_tuesday', 'trips_wednesday', 'trips_thursday', 'trips_friday',
            'trips_saturday', 'trips_sunday', 
            'zev_charging_infrastrucutre', 'zev_notes', 'pct_zev_service', 'num_zev'] 

class AgencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Agency 

        fields = ['agency_id', 'agency_name', 'agency_url', 'agency_timezone', 
        		'agency_lang', 'agency_phone', 'agency_fare_url', 'agency_email',
        		'num_vehicles', 'num_zero_emission_vehicles'] 