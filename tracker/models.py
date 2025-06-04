from django.db import models

class Expense(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    date = models.DateField()

    def __str__(self):
        return self.name
# This model defines an Expense with fields for name, amount, category, and date.
# The __str__ method returns the name of the expense for easy identification in the admin interface.