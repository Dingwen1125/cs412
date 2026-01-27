from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import time
import random  
# Create your views here.
def home_page(request):
    template = "hw/home.html"
    context = {'current_time': time.ctime(),
            'letter1':chr(random.randint(65,90)),
            'letter2' : chr(random.randint(65,90)),
            'number' : random.randint(1,10),}
    return render(request, template, context)

def about(request):
    template = "hw/about.html"
    context = {'current_time': time.ctime(),
            'letter1':chr(random.randint(65,90)),
            'letter2' : chr(random.randint(65,90)),
            'number' : random.randint(1,10),}
    return render(request, template, context)