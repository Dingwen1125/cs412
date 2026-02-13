# File: views.py
# Author: Dingwen Yang(laoba@bu.edu), 2/12/2026
# Description: Define list/detail views for MiniInsta profiles.

from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Profile
# Create your views here.

class ShowAllView(ListView):
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"

class ProfileDetailView(DetailView):
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"
