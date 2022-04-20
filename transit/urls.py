from django.urls import path

from . import views

urlpatterns = [
    path('agency/', views.agency_list, name='agency_list'),
    path('agency/<agency_id>', views.agency_detail),
    path('agency/<agency_id>/route', views.route_list, name='route_list'),
    path('', views.index, name='index'),
]