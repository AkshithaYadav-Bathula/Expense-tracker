from django.shortcuts import render, redirect
from .models import Expense
from .forms import ExpenseForm

def home(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ExpenseForm()
    
    expenses = Expense.objects.all()
    return render(request, 'tracker/home.html', {'form': form, 'expenses': expenses})
