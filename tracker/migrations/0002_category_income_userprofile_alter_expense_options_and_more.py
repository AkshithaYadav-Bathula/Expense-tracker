# Generated by Django 5.1.6 on 2025-06-16 17:30

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('color', models.CharField(default='#007bff', help_text='Hex color code', max_length=7)),
                ('icon', models.CharField(default='fas fa-money-bill-wave', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Income',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('source', models.CharField(choices=[('salary', 'Salary'), ('freelance', 'Freelance'), ('business', 'Business'), ('investment', 'Investment'), ('gift', 'Gift'), ('bonus', 'Bonus'), ('other', 'Other')], default='salary', max_length=20)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('is_recurring', models.BooleanField(default=False)),
                ('recurring_period', models.CharField(blank=True, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('currency', models.CharField(default='INR', max_length=3)),
                ('monthly_budget', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('timezone', models.CharField(default='Asia/Kolkata', max_length=50)),
                ('email_notifications', models.BooleanField(default=True)),
                ('budget_alerts', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='expense',
            options={'ordering': ['-date', '-created_at']},
        ),
        migrations.RemoveField(
            model_name='expense',
            name='name',
        ),
        migrations.AddField(
            model_name='expense',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='expense',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='expense',
            name='is_recurring',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='expense',
            name='location',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='expense',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'Cash'), ('card', 'Debit/Credit Card'), ('upi', 'UPI'), ('netbanking', 'Net Banking'), ('wallet', 'Digital Wallet'), ('cheque', 'Cheque'), ('other', 'Other')], default='cash', max_length=20),
        ),
        migrations.AddField(
            model_name='expense',
            name='receipt_image',
            field=models.ImageField(blank=True, null=True, upload_to='receipts/'),
        ),
        migrations.AddField(
            model_name='expense',
            name='recurring_period',
            field=models.CharField(blank=True, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='expense',
            name='tags',
            field=models.CharField(blank=True, help_text='Comma-separated tags', max_length=200),
        ),
        migrations.AddField(
            model_name='expense',
            name='title',
            field=models.CharField(default='Untitled Expense', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='expense',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='expense',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expense',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='expense',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('period_type', models.CharField(choices=[('monthly', 'Monthly'), ('weekly', 'Weekly'), ('daily', 'Daily'), ('yearly', 'Yearly')], default='monthly', max_length=20)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to='tracker.category')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='tracker.category'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['user', 'date'], name='tracker_exp_user_id_bcd9ed_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['category', 'date'], name='tracker_exp_categor_09ac2c_idx'),
        ),
        migrations.AddField(
            model_name='income',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incomes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='budget',
            unique_together={('user', 'category', 'period_type')},
        ),
    ]
