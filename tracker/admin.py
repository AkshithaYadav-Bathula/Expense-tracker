from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Category, Expense, Income, Budget, UserProfile

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'icon', 'created_at', 'expense_count']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 50%; display: inline-block;"></div>',
            obj.color
        )
    color_display.short_description = 'Color'
    
    def expense_count(self, obj):
        return obj.expenses.count()
    expense_count.short_description = 'Total Expenses'

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'amount', 'category', 'date', 'payment_method', 'is_recurring']
    list_filter = ['category', 'payment_method', 'is_recurring', 'date', 'created_at']
    search_fields = ['title', 'description', 'tags', 'location', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'amount', 'category', 'date')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'receipt_image')
        }),
        ('Recurring', {
            'fields': ('is_recurring', 'recurring_period'),
            'classes': ('collapse',)
        }),
        ('Additional Info', {
            'fields': ('tags', 'location'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'category')

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'amount', 'source', 'date', 'is_recurring']
    list_filter = ['source', 'is_recurring', 'date', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'amount', 'source', 'date')
        }),
        ('Recurring', {
            'fields': ('is_recurring', 'recurring_period'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'period_type', 'start_date', 'is_active', 'spent_amount', 'remaining_amount']
    list_filter = ['period_type', 'is_active', 'start_date', 'created_at']
    search_fields = ['user__username', 'category__name']
    readonly_fields = ['created_at', 'updated_at', 'spent_amount', 'remaining_amount']
    list_per_page = 25
    
    def spent_amount(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        current_month = timezone.now().replace(day=1)
        next_month = (current_month + timedelta(days=32)).replace(day=1)
        
        spent = obj.category.expenses.filter(
            user=obj.user,
            date__gte=current_month,
            date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return f"₹{spent}"
    spent_amount.short_description = 'Spent This Month'
    
    def remaining_amount(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        current_month = timezone.now().replace(day=1)
        next_month = (current_month + timedelta(days=32)).replace(day=1)
        
        spent = obj.category.expenses.filter(
            user=obj.user,
            date__gte=current_month,
            date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        remaining = obj.amount - spent
        color = 'red' if remaining < 0 else 'green'
        return format_html(
            '<span style="color: {};">₹{}</span>',
            color, remaining
        )
    remaining_amount.short_description = 'Remaining'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'monthly_budget', 'email_notifications', 'budget_alerts', 'created_at']
    list_filter = ['email_notifications', 'budget_alerts', 'currency', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'avatar', 'phone', 'date_of_birth')
        }),
        ('Preferences', {
            'fields': ('currency', 'timezone', 'monthly_budget')
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'budget_alerts')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

# Custom admin site settings
admin.site.site_header = "ExpenseTracker Administration"
admin.site.site_title = "ExpenseTracker Admin"
admin.site.index_title = "Welcome to ExpenseTracker Admin Panel"