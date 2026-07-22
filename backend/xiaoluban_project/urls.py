"""
Xiaoluban URL Configuration
"""
from django.urls import path, include

urlpatterns = [
    path('api/', include('xiaoluban_api.urls')),
]