from django.urls import path

from . import views

urlpatterns = [
    path('agency/', views.agency_list),
    path('agency/<id>', views.agency_detail),
    path('', views.index, name='index'),
]