from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncDay
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
import csv
from io import StringIO
from .models import Expense, Income, Category, Budget, UserProfile
from .forms import (CustomUserCreationForm, ExpenseForm, IncomeForm, 
                   CategoryForm, BudgetForm, UserProfileForm, ExpenseFilterForm)

def home(request):
    """Landing page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'tracker/home.html')

@login_required
def dashboard(request):
    """Main dashboard with overview"""
    # Get current month data
    current_month = timezone.now().replace(day=1)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    
    # Total expenses and income for current month
    monthly_expenses = Expense.objects.filter(
        user=request.user,
        date__gte=current_month,
        date__lt=next_month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    monthly_income = Income.objects.filter(
        user=request.user,
        date__gte=current_month,
        date__lt=next_month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Recent transactions
    recent_expenses = Expense.objects.filter(user=request.user)[:5]
    recent_income = Income.objects.filter(user=request.user)[:3]
    
    # Category-wise spending for current month
    category_expenses = Expense.objects.filter(
        user=request.user,
        date__gte=current_month,
        date__lt=next_month
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')[:6]
    
    # Budget status
    budgets = Budget.objects.filter(user=request.user, is_active=True)
    budget_status = []
    for budget in budgets:
        spent = Expense.objects.filter(
            user=request.user,
            category=budget.category,
            date__gte=current_month,
            date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        percentage = float(spent / budget.amount * 100) if budget.amount > 0 else 0
        budget_status.append({
            'budget': budget,
            'spent': spent,
            'remaining': budget.amount - spent,
            'percentage': percentage,
            'status': 'danger' if percentage > 90 else 'warning' if percentage > 70 else 'success'
        })
    
    # Quick stats
    total_expenses = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_income = Income.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    context = {
        'monthly_expenses': monthly_expenses,
        'monthly_income': monthly_income,
        'monthly_balance': monthly_income - monthly_expenses,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'total_balance': total_income - total_expenses,
        'recent_expenses': recent_expenses,
        'recent_income': recent_income,
        'category_expenses': category_expenses,
        'budget_status': budget_status,
        'current_month': current_month.strftime('%B %Y'),
    }
    
    return render(request, 'tracker/dashboard.html', context)

def register(request):
    """User registration"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to ExpenseTracker.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'tracker/auth/register.html', {'form': form})

@login_required
def profile(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'tracker/profile.html', {'profile': profile})

@login_required
def edit_profile(request):
    """Edit user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'tracker/edit_profile.html', {'form': form})

@login_required
def expense_list(request):
    """List all expenses with filtering"""
    expenses = Expense.objects.filter(user=request.user)
    filter_form = ExpenseFilterForm(request.GET)
    
    # Apply filters
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('date_from'):
            expenses = expenses.filter(date__gte=filter_form.cleaned_data['date_from'])
        if filter_form.cleaned_data.get('date_to'):
            expenses = expenses.filter(date__lte=filter_form.cleaned_data['date_to'])
        if filter_form.cleaned_data.get('category'):
            expenses = expenses.filter(category=filter_form.cleaned_data['category'])
        if filter_form.cleaned_data.get('payment_method'):
            expenses = expenses.filter(payment_method=filter_form.cleaned_data['payment_method'])
        if filter_form.cleaned_data.get('amount_min'):
            expenses = expenses.filter(amount__gte=filter_form.cleaned_data['amount_min'])
        if filter_form.cleaned_data.get('amount_max'):
            expenses = expenses.filter(amount__lte=filter_form.cleaned_data['amount_max'])
    
    # Pagination
    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate totals
    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'total_amount': total_amount,
        'expenses_count': expenses.count(),
    }
    
    return render(request, 'tracker/expenses/list.html', context)

@login_required
def add_expense(request):
    """Add new expense"""
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, f'Expense "{expense.title}" added successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    
    return render(request, 'tracker/expenses/form.html', {
        'form': form,
        'title': 'Add Expense',
        'button_text': 'Add Expense'
    })

@login_required
def edit_expense(request, pk):
    """Edit existing expense"""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, f'Expense "{expense.title}" updated successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    
    return render(request, 'tracker/expenses/form.html', {
        'form': form,
        'title': 'Edit Expense',
        'button_text': 'Update Expense',
        'expense': expense
    })

@login_required
def delete_expense(request, pk):
    """Delete expense"""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'POST':
        expense_title = expense.title
        expense.delete()
        messages.success(request, f'Expense "{expense_title}" deleted successfully!')
        return redirect('expense_list')
    
    return render(request, 'tracker/expenses/delete.html', {'expense': expense})

@login_required
def expense_detail(request, pk):
    """Expense detail view"""
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    return render(request, 'tracker/expenses/detail.html', {'expense': expense})

@login_required
def income_list(request):
    """List all income"""
    incomes = Income.objects.filter(user=request.user)
    
    # Pagination
    paginator = Paginator(incomes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate totals
    total_amount = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    context = {
        'page_obj': page_obj,
        'total_amount': total_amount,
        'incomes_count': incomes.count(),
    }
    
    return render(request, 'tracker/income/list.html', context)

@login_required
def add_income(request):
    """Add new income"""
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, f'Income "{income.title}" added successfully!')
            return redirect('income_list')
    else:
        form = IncomeForm()
    
    return render(request, 'tracker/income/form.html', {
        'form': form,
        'title': 'Add Income',
        'button_text': 'Add Income'
    })

@login_required
def edit_income(request, pk):
    """Edit existing income"""
    income = get_object_or_404(Income, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, f'Income "{income.title}" updated successfully!')
            return redirect('income_list')
    else:
        form = IncomeForm(instance=income)
    
    return render(request, 'tracker/income/form.html', {
        'form': form,
        'title': 'Edit Income',
        'button_text': 'Update Income',
        'income': income
    })

@login_required
def delete_income(request, pk):
    """Delete income"""
    income = get_object_or_404(Income, pk=pk, user=request.user)
    
    if request.method == 'POST':
        income_title = income.title
        income.delete()
        messages.success(request, f'Income "{income_title}" deleted successfully!')
        return redirect('income_list')
    
    return render(request, 'tracker/income/delete.html', {'income': income})

@login_required
def category_list(request):
    """List all categories"""
    categories = Category.objects.all()
    return render(request, 'tracker/categories/list.html', {'categories': categories})

@login_required
def add_category(request):
    """Add new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" added successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'tracker/categories/form.html', {
        'form': form,
        'title': 'Add Category',
        'button_text': 'Add Category'
    })

@login_required
def edit_category(request, pk):
    """Edit existing category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'tracker/categories/form.html', {
        'form': form,
        'title': 'Edit Category',
        'button_text': 'Update Category',
        'category': category
    })

@login_required
def delete_category(request, pk):
    """Delete category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('category_list')
    
    return render(request, 'tracker/categories/delete.html', {'category': category})

@login_required
def budget_list(request):
    """List all budgets"""
    budgets = Budget.objects.filter(user=request.user)
    
    # Calculate spent amounts for each budget
    budget_data = []
    current_month = timezone.now().replace(day=1)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    
    for budget in budgets:
        spent = Expense.objects.filter(
            user=request.user,
            category=budget.category,
            date__gte=current_month,
            date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        percentage = float(spent / budget.amount * 100) if budget.amount > 0 else 0
        budget_data.append({
            'budget': budget,
            'spent': spent,
            'remaining': budget.amount - spent,
            'percentage': percentage,
            'status': 'danger' if percentage > 90 else 'warning' if percentage > 70 else 'success'
        })
    
    return render(request, 'tracker/budgets/list.html', {'budget_data': budget_data})

@login_required
def add_budget(request):
    """Add new budget"""
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, f'Budget for "{budget.category.name}" added successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm()
    
    return render(request, 'tracker/budgets/form.html', {
        'form': form,
        'title': 'Add Budget',
        'button_text': 'Add Budget'
    })

@login_required
def edit_budget(request, pk):
    """Edit existing budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, f'Budget for "{budget.category.name}" updated successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget)
    
    return render(request, 'tracker/budgets/form.html', {
        'form': form,
        'title': 'Edit Budget',
        'button_text': 'Update Budget',
        'budget': budget
    })

@login_required
def delete_budget(request, pk):
    """Delete budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    if request.method == 'POST':
        category_name = budget.category.name
        budget.delete()
        messages.success(request, f'Budget for "{category_name}" deleted successfully!')
        return redirect('budget_list')
    
    return render(request, 'tracker/budgets/delete.html', {'budget': budget})

@login_required
def analytics(request):
    """Analytics dashboard"""
    # Monthly expenses for the current year
    current_year = timezone.now().year
    monthly_data = Expense.objects.filter(
        user=request.user,
        date__year=current_year
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Category breakdown
    category_data = Expense.objects.filter(
        user=request.user
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Payment method breakdown
    payment_data = Expense.objects.filter(
        user=request.user
    ).values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Top expenses
    top_expenses = Expense.objects.filter(user=request.user).order_by('-amount')[:10]
    
    # Recent trends (last 30 days daily)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    daily_trends = Expense.objects.filter(
        user=request.user,
        date__gte=thirty_days_ago
    ).annotate(
        day=TruncDay('date')
    ).values('day').annotate(
        total=Sum('amount')
    ).order_by('day')
    
    context = {
        'monthly_data': list(monthly_data),
        'category_data': list(category_data),
        'payment_data': list(payment_data),
        'top_expenses': top_expenses,
        'daily_trends': list(daily_trends),
        'current_year': current_year,
    }
    
    return render(request, 'tracker/analytics.html', context)

@login_required
def reports(request):
    """Reports page"""
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        # Default to current month
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today
    
    # Filter expenses and income
    expenses = Expense.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    )
    
    incomes = Income.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    )
    
    # Calculate totals
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_income = incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    net_savings = total_income - total_expenses
    
    # Category breakdown
    category_breakdown = expenses.values(
        'category__name', 'category__color'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Income source breakdown
    income_breakdown = incomes.values('source').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'expenses': expenses,
        'incomes': incomes,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'net_savings': net_savings,
        'category_breakdown': category_breakdown,
        'income_breakdown': income_breakdown,
        'expenses_count': expenses.count(),
        'incomes_count': incomes.count(),
    }
    
    return render(request, 'tracker/reports.html', context)

@login_required
def export_expenses(request):
    """Export expenses to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Title', 'Category', 'Amount', 'Payment Method', 
        'Description', 'Tags', 'Location'
    ])
    
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    for expense in expenses:
        writer.writerow([
            expense.date,
            expense.title,
            expense.category.name,
            expense.amount,
            expense.get_payment_method_display(),
            expense.description or '',
            expense.tags or '',
            expense.location or '',
        ])
    
    return response

@login_required
def search_expenses(request):
    """Search expenses"""
    query = request.GET.get('q', '')
    expenses = Expense.objects.filter(user=request.user)
    
    if query:
        expenses = expenses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(location__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'total_results': expenses.count(),
    }
    
    return render(request, 'tracker/search_results.html', context)

# API Views for AJAX requests
@login_required
def expense_chart_data(request):
    """API endpoint for expense chart data"""
    expenses = Expense.objects.filter(user=request.user)
    
    # Get last 6 months data
    monthly_data = []
    for i in range(6):
        date = timezone.now() - timedelta(days=30*i)
        month_start = date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        total = expenses.filter(
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'total': float(total)
        })
    
    return JsonResponse({'data': list(reversed(monthly_data))})

@login_required
def category_chart_data(request):
    """API endpoint for category chart data"""
    category_data = Expense.objects.filter(
        user=request.user
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')[:10]
    
    data = {
        'labels': [item['category__name'] for item in category_data],
        'data': [float(item['total']) for item in category_data],
        'colors': [item['category__color'] for item in category_data]
    }
    
    return JsonResponse(data)

@login_required
def monthly_trend_data(request):
    """API endpoint for monthly trend data"""
    # Get last 12 months data
    monthly_expenses = []
    monthly_income = []
    labels = []
    
    for i in range(12):
        date = timezone.now() - timedelta(days=30*i)
        month_start = date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        expense_total = Expense.objects.filter(
            user=request.user,
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        income_total = Income.objects.filter(
            user=request.user,
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_expenses.append(float(expense_total))
        monthly_income.append(float(income_total))
        labels.append(month_start.strftime('%b %Y'))
    
    data = {
        'labels': list(reversed(labels)),
        'expenses': list(reversed(monthly_expenses)),
        'income': list(reversed(monthly_income))
    }
    
    return JsonResponse(data)