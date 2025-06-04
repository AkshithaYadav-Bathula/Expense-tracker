from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tracker.urls')),
]
# This file defines the URL patterns for the entire Django project.
# It includes the admin site URLs and the URLs from the tracker app.