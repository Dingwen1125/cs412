from django.shortcuts import render
import time

# Create your views here.
def home_page(request):
    template = "quote/home.html"
    context = {'current_time': time.ctime()}
    return render(request, template, context)

def quoteOf(request):
    template = "quote/quoteOf.html"
    context = {'current_time': time.ctime()}
    return render(request, template, context)

def show_all(request):
    template = "quote/showAll.html"
    context = {'current_time': time.ctime()}
    return render(request, template, context)

def about(request):
    template = "quote/about.html"
    context = {'current_time': time.ctime()}
    return render(request, template, context)