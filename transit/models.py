from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf.global_settings import LANGUAGES
import uuid
import pytz
from rest_framework_mvt.managers import MVTManager

TIMEZONES = [tuple([i, i]) for i in pytz.all_timezones]

# see gtfs documentation for reference: https://developers.google.com/transit/gtfs/reference#routestxt
ROUTE_TYPES = [
    ("0", "Tram, Streetcar, Light rail"),
    ("1", "Subway, Metro"),
    ("2", "Rail"),
    ("3", "Bus"),
    ("4", "Ferry"),
    ("5", "Cable Car"),
    ("6", "Gondola"),
    ("7", "Funicular"),
]

class DataSource(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, blank=False)

    ### Upload Tracking fields
    last_upload = models.DateTimeField(null=True)

    ### Mobility Database fields 
    mdb_source_id = models.CharField(max_length=32, blank=True)
    location_country_code = models.CharField(max_length=32, blank=True)
    location_subdivision_name = models.CharField(max_length=100, blank=True)
    location_municipality = models.CharField(max_length=100, blank=True)
    provider = models.CharField(max_length=250, blank=True)
    urls_direct_download = models.CharField(max_length=250, blank=True)
    urls_authentication_type = models.CharField(max_length=100, blank=True)
    urls_authentication_info = models.CharField(max_length=100, blank=True)
    urls_api_key_parameter_name = models.CharField(max_length=100, blank=True)
    urls_latest = models.CharField(max_length=250, blank=True)
    urls_license = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.mdb_source_id + ":" + self.provider

class Agency(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, blank=False)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, null=True)

    ### from gtfs
    agency_id = models.CharField(max_length=100, blank=True, default="")
    agency_name = models.CharField(max_length=100)  # required
    agency_url = models.CharField(max_length=100)  # required
    agency_timezone = models.CharField(
        max_length=50, blank=True, choices=TIMEZONES, default=""
    )
    agency_lang = models.CharField(
        max_length=50, blank=True, choices=LANGUAGES, default=""
    )
    agency_phone = models.CharField(max_length=20, blank=True, default="")
    agency_fare_url = models.CharField(max_length=100, blank=True, default="")
    agency_email = models.EmailField(max_length=100, blank=True, default="")

    ### managed in app
    num_vehicles = models.IntegerField(blank=True, null=True)
    num_zero_emission_vehicles = models.IntegerField(blank=True, null=True)
    gtfs_url = models.CharField(
        max_length=100, blank=True, default=""
    )  ## for management process
    accepted_domains = ArrayField(
        models.CharField(max_length=100), blank=True, default=list
    )

    def __str__(self):
        return self.agency_name + ":" + self.agency_id


class Route(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)

    # from gtfs
    route_id = models.CharField(max_length=50)  # required
    route_short_name = models.CharField(max_length=50, blank=True)
    route_long_name = models.CharField(max_length=100, blank=True)
    route_desc = models.CharField(max_length=500, blank=True)

    # required, this will always be 3
    route_type = models.CharField(max_length=50, choices=ROUTE_TYPES)
    route_url = models.CharField(max_length=100, blank=True)
    route_color = models.CharField(max_length=50, blank=True)
    route_text_color = models.CharField(max_length=50, blank=True)
    route_sort_order = models.CharField(max_length=50, blank=True)

    # GeoDjango-specific: a geometry field
    geometry = models.MultiLineStringField(srid=4326, blank=True, null=True)

    route_distance = models.FloatField(blank=True, null=True)  ### calculated

    trips_monday = models.IntegerField(blank=True)
    trips_tuesday = models.IntegerField(blank=True)
    trips_wednesday = models.IntegerField(blank=True)
    trips_thursday = models.IntegerField(blank=True)
    trips_friday = models.IntegerField(blank=True)
    trips_saturday = models.IntegerField(blank=True)
    trips_sunday = models.IntegerField(blank=True)

    ### user managed fields
    zev_charging_infrastructure = models.BooleanField(default=False)
    zev_notes = models.TextField(blank=True, null=True)
    pct_zev_service = models.FloatField(blank=True, null=True)
    num_zev = models.IntegerField(blank=True, null=True)

    ### managed by djangorestframework-mvt
    vector_tiles = MVTManager(geo_col="geometry")
    objects = models.Manager()

    # Returns the string representation of the model.
    def __str__(self):
        return self.route_long_name + " (" + self.route_id + ")"

