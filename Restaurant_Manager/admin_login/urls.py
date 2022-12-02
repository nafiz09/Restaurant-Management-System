from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login_view'),
    path('managers/', views.man_table, name='table_view'),
    path('admin_signup/', views.signup, name='form_view'),
    path('not_lgin/', views.not_lgin, name='not_lgin_view'),
    path('home/', views.home, name='home_view'),
    path('logout/', views.logout, name='lgout_view'),
    path('employees/', views.emp_table, name='emp_view'),
    path('add_employee/', views.add_emp, name='add_emp'),
]
