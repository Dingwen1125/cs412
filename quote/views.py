# File: hello_world.py
# Author: Dingwen Yang (laoba@bu.edu), 1/27/2025
# Description: rendering each pages in the app

from django.shortcuts import render
import time
import random

# tow array conatning quotes and images for the randaom chose later
quotes = ["The most merciful thing in the world is the inability of the human mind to correlate all its contents",
            "That is not dead which can eternal lie,<br> And with strange aeons even death may die.",
            "Man is the measure of all things—only by his ignorance of other measures."]
images = ["images/hp1.pic.jpg", "images/hp2.pic.jpg", "images/hp3.pic.jpg", "images/hp4.pic.jpg", "images/hp5.pic.jpg"]
# Create your views here.
def home_page(request):
    """
    return the current time and the home page
    """
    template = "quote/home.html"
    context = {'current_time': time.ctime(), "chosen_quote": random.choice(quotes), "chosen_image": random.choice(images)} #choose one quote and image randomly
    return render(request, template, context)

def quoteOf(request):
    """
    return the current time and the 'quote of the day' page
    """
    template = "quote/quoteOf.html"
    context = {'current_time': time.ctime(), "chosen_quote": random.choice(quotes), "chosen_image": random.choice(images)}
    return render(request, template, context)

def show_all(request):
    """
    return the current time and the 'Show all' page
    """
    template = "quote/showAll.html"
    context = {'current_time': time.ctime(), "quotes": quotes, "images": images} #load all the images and quotes for showing all of them in this page
    return render(request, template, context)

def about(request):
    """
    return the current time and the about page
    """
    template = "quote/about.html"
    context = {'current_time': time.ctime()}
    return render(request, template, context)