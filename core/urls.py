from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointment_booking, name='appointment_booking'),
    path('check-in/', views.check_in, name='check_in'),
    path('billing/', views.billing, name='billing'),
    path('stats/', views.stats_view, name='stats'),
]
