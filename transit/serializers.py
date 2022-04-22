from rest_framework import serializers
from .models import Route, Agency


class RouteSerializer(serializers.ModelSerializer):

    agency_name = serializers.CharField(
        read_only=False, source="agency_id.agency_name", required=False
    )
    agency_id = serializers.CharField(
        read_only=False, source="agency_id.id", required=False
    )

    class Meta:
        model = Route

        fields = [
            "id",
            "route_id",
            "agency_name",
            "agency_id",
            "route_short_name",
            "route_long_name",
            "route_desc",
            "route_type",
            "route_url",
            "route_color",
            "route_distance",
            "trips_monday",
            "trips_tuesday",
            "trips_wednesday",
            "trips_thursday",
            "trips_friday",
            "trips_saturday",
            "trips_sunday",
            "zev_charging_infrastrucutre",
            "zev_notes",
            "pct_zev_service",
            "num_zev",
        ]

    def create(self, validated_data):
        agency_id = validated_data.pop("agency_id")
        agency = Agency.objects.get(id=agency_id["id"])
        route = Route.objects.create(agency_id=agency, **validated_data)
        return route


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency

        fields = [
            "id",
            "agency_id",
            "agency_name",
            "agency_url",
            "agency_timezone",
            "agency_lang",
            "agency_phone",
            "agency_fare_url",
            "agency_email",
            "num_vehicles",
            "num_zero_emission_vehicles",
        ]
