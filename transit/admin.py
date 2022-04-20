from django.contrib import admin

# Register your models here.

from .models import Agency, Route

class RouteInline(admin.StackedInline):
	model = Route
	

class AgencyAdmin(admin.ModelAdmin):
	search_fields = ['agency_name']
	# inlines = [
	# 	RouteInline,
	# ]
	list_display = ['agency_name','gtfs_url', 'num_routes','agency_url', 'num_vehicles', 'num_zero_emission_vehicles']

	def num_routes(self, obj):
		return obj.route_set.count()

	class Meta:
		verbose_name_plural = "Agencies"


admin.site.register(Agency, AgencyAdmin)

class RouteAdmin(admin.ModelAdmin):
	ordering = ['agency_id']
	list_display = ['route_id', 'agency_id', 'route_short_name', 'route_long_name' ]
	search_fields = ['route_short_name', 'route_long_name', 'route_id']

admin.site.register(Route, RouteAdmin)