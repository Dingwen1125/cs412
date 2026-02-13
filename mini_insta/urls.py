# File: urls.py
# Author: Dingwen Yang(laoba@bu.edu), 2/12/2026
# Description: Map MiniInsta URL routes to views.

from django.urls import path
from .views import ShowAllView, ProfileDetailView
urlpatterns = [
    path('', ShowAllView.as_view(), name="show_all"),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name="show_profile"),
]
