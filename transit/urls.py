from django.urls import path

from . import views

urlpatterns = [
    path('agency/', views.agency_list),
    path('', views.index, name='index'),
]