from django.contrib import admin

from .models import Agency, Route, DataSource


class AgencyAdmin(admin.ModelAdmin):
    search_fields = ["agency_name"]
    list_display = [
        "agency_name",
        "name",
        "num_routes",
        "agency_url",
        "num_vehicles",
        "num_zero_emission_vehicles",
    ]

    def num_routes(self, obj):
        return obj.route_set.count()

    class Meta:
        verbose_name_plural = "Agencies"


admin.site.register(Agency, AgencyAdmin)


class RouteAdmin(admin.ModelAdmin):
    ordering = ["agency_id"]
    list_display = ["route_id", "agency_id", "route_short_name", "route_long_name"]
    search_fields = ["route_short_name", "route_long_name", "route_id"]


admin.site.register(Route, RouteAdmin)


class DataSourceAdmin(admin.ModelAdmin):
    ordering = ["mdb_source_id"]
    list_display = ["mdb_source_id", "provider", "location_country_code", "location_subdivision_name", "location_municipality", "urls_latest"]
    search_fields = ["provider", "location_country_code", "location_subdivision_name", "location_municipality"]

admin.site.register(DataSource, DataSourceAdmin)