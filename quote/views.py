# File: hello_world.py
# Author: Dingwen Yang (laoba@bu.edu), 1/27/2025
# Description: rendering each pages in the app

from django.shortcuts import render
import time

# Create your views here.
def home_page(request):
    """
    return the current time and the home page
    """
    template = "quote/home.html"
    context = {'current_time': time.ctime()}
    return render(request, template, context)

def quoteOf(request):
    """
    return the current time and the 'quote of the day' page
    """
    template = "quote/quoteOf.html"
    context = {'current_time': time.ctime()}
    return render(request, template, context)

def show_all(request):
    """
    return the current time and the 'Show all' page
    """
    template = "quote/showAll.html"
    context = {'current_time': time.ctime()}
    return render(request, template, context)

def about(request):
    """
    return the current time and the about page
    """
    template = "quote/about.html"
    context = {'current_time': time.ctime()}
    return render(request, template, context)