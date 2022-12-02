from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.place_order, name='place_order'),
    path('confirm_order/', views.confirm_order, name='confirm_order'),
]
