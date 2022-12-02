from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_menu, name='view_menu'),
    path('add_item/', views.add_menu_item, name='add_item'),
]
