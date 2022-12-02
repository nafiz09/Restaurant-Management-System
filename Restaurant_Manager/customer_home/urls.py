from django.urls import path
from . import views

urlpatterns = [
        path('', views.customer_home, name="cus_home"),
        path('logout/', views.logout, name="logout"),
]
