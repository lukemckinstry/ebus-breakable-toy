from django.urls import path
from .views import AgencyViewSet, RouteViewSet

from . import views

agency_list = AgencyViewSet.as_view({"get": "list", "post": "create"})
agency_detail = AgencyViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)
route_create = RouteViewSet.as_view({"post": "create"})
route_list = RouteViewSet.as_view({"get": "list"})
route_detail = RouteViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)


urlpatterns = [
    path("agency/", agency_list, name="agency-list"),
    path("agency/<str:pk>/", agency_detail, name="agency-detail"),
    path("agency/<str:agency_pk>/route", route_list, name="route-list"),
    path("route/", route_create, name="route-create"),
    path("route/<str:pk>/", route_detail, name="route-detail"),
    path("", views.index, name="index"),
]
