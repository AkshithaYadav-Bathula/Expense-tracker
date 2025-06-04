# expensetracker/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tracker.urls')),
]
# This file defines the URL patterns for the Expense Tracker application.
# It includes the admin site and the URLs from the tracker app.