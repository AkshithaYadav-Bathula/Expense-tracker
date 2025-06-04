from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tracker.urls')),  # include tracker app urls
]
# This file defines the URL patterns for the Expense Tracker project.
# The admin interface is accessible at 'admin/' and the tracker app's URLs are included at the root URL.