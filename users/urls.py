from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_settings, name='profile_settings'),
    path('register/', views.register, name='register'),
]
