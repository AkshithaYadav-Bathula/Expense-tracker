from django.shortcuts import render
from .models import Expense

def home(request):
    expenses = Expense.objects.all().order_by('-date')  # latest first
    return render(request, 'tracker/home.html', {'expenses': expenses})

# This view retrieves all Expense objects from the database, ordered by date in descending order.
# It then renders the 'home.html' template, passing the expenses as context.