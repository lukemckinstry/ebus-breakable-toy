from django.urls import path
from .views import AgencyViewSet, RouteViewSet, RouteBatchViewSet, DataSourceViewSet, DataSourceUpdateView
from .models import Route
from rest_framework_mvt.views import mvt_view_factory

from . import views

data_source_list = DataSourceViewSet.as_view({"get": "list", "post": "create"})
data_source_detail = DataSourceViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)
data_source_update = DataSourceUpdateView.as_view()
agency_list = AgencyViewSet.as_view({"get": "list", "post": "create"})
agency_detail = AgencyViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)
route_create = RouteViewSet.as_view({"post": "create"})
route_list = RouteViewSet.as_view({"get": "list"})
route_detail = RouteViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)
route_batch_list = RouteBatchViewSet.as_view({"post": "create","get":"list"})
route_batch_detail = RouteBatchViewSet.as_view({"put": "update"})


urlpatterns = [
    path("datasource/", data_source_list, name="data-source-list"),
    path("datasource/<str:pk>/", data_source_detail, name="data-source-detail"),
    path("datasource/<str:pk>/update", data_source_update, name="data-source-update"),
    path("datasource/<str:pk>/agency/", agency_list, name="data-source-agency-list"),
    path("agency/", agency_list, name="agency-list"),
    path("agency/<str:pk>/", agency_detail, name="agency-detail"),
    path("agency/<str:agency_pk>/route", route_list, name="route-list"),
    path("agency/<str:agency_pk>/batch/route", route_batch_list, name="route-batch-list"),
    path("route/tiles", mvt_view_factory(Route)),
    path("route/<str:pk>/", route_detail, name="route-detail"),
    path("route/batch/<str:pk>/", route_batch_detail, name="route-batch-detail"),
    path("route/bbox/<str:pk>/", views.route_bbox, name="route-bbox"),
    path("basicmap/", views.basic_map),
    path("route/", route_create, name="route-create"),
    path("", views.index, name="index"),
]
