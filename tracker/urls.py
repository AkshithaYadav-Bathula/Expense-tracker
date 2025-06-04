from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
]
# This file defines the URL patterns for the tracker app.
# The home view is mapped to the root URL of the app.