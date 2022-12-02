from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.expenses_list, name='expenses'),
    path('add_entry/', views.add_entry, name='add_entry'),
]
