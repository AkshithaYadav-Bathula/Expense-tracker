from django.contrib import admin
from .models import Expense

admin.site.register(Expense)
# This file registers the Expense model with the Django admin site.
# This allows the Expense model to be managed through the Django admin interface.