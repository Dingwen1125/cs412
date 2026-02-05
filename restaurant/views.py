from django.shortcuts import render
import time
import random;

all_food = [{"name": "Fries", "price": 5},
            {"name": "Burger", "price": 7},
            {"name": "coke", "price": 3},
            {"name": "Milkshake", "price": 4}]

# Create your views here.
def home(request):
    template = "restaurant/home.html"
    context = {'current_time': time.ctime()}
    return render(request, template, context)

def order(request):
    
    special = random.choice(all_food)
    template = "restaurant/order.html"
    context = {'dailySpecial': special, 'current_time': time.ctime(), 'all_food': all_food}
    return render(request,template, context)

def submit(request):
    template = "restaurant/confirmation.html"
    if request.POST:
        chosen = request.POST.getlist("chosen_food")
        special = request.POST.get("special")
        requirement = request.POST.get("requirement")
        name = request.POST.get("name", "")
        phone = request.POST.get("phone", "")
        email = request.POST.get("email", "")

        total = 0
        for food in all_food:
            if food["name"] in chosen:
                total += food["price"]
            if special and food["name"] == special:
                total += food["price"]
    context = {'chosen': chosen, 'special': special, 'requirement':requirement, 'name': name, 'phone':phone, 'email': email, 'total': total, 'current_time': time.ctime()}
    return render(request,template, context)