from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.pending_list, name='pending_list'),
]
