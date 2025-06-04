from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello, welcome to Expense Tracker!")
