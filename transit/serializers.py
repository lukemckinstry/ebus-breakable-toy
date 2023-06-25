from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Route, Agency, DataSource


class RouteSerializer(serializers.ModelSerializer):

    agency = serializers.PrimaryKeyRelatedField(queryset=Agency.objects.all())


    class Meta:
        model = Route

        fields = [
            "id",
            "route_id",
            "agency",
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
            "zev_charging_infrastructure",
            "zev_notes",
            "pct_zev_service",
            "num_zev",
        ]

class AgencySerializer(serializers.ModelSerializer):
    data_source = serializers.PrimaryKeyRelatedField(queryset=DataSource.objects.all())

    class Meta:
        model = Agency
        fields = '__all__'

        # fields = [
        #     "id",
        #     "agency_id",
        #     "agency_name",
        #     "agency_url",
        #     "agency_timezone",
        #     "agency_lang",
        #     "agency_phone",
        #     "agency_fare_url",
        #     "agency_email",
        #     "num_vehicles",
        #     "num_zero_emission_vehicles",
        # ]

class DataSourceSerializer(serializers.ModelSerializer):
    agency_records = serializers.SerializerMethodField()

    def get_agency_records(self, data_source):
        agency_records  = Agency.objects.filter(data_source_id=data_source.id)
        return AgencySerializer(agency_records, many=True).data

    class Meta:
        model = DataSource
        fields = "__all__"

class RouteBatchSerializer(GeoFeatureModelSerializer):
    agency = serializers.PrimaryKeyRelatedField(queryset=Agency.objects.all())

    class Meta:
        model = Route
        geo_field = "geometry"
        fields = [
            "id",
            "route_id",
            "agency",
            "route_short_name",
            "route_long_name",
            "route_desc",
            "route_type",
            "route_url",
            "route_color",
            "route_text_color",
            "route_sort_order",
            "geometry",
            "route_distance",
            "trips_monday",
            "trips_tuesday",
            "trips_wednesday",
            "trips_thursday",
            "trips_friday",
            "trips_saturday",
            "trips_sunday",
            "zev_charging_infrastructure",
            "zev_notes",
            "pct_zev_service",
            "num_zev",
        ]
