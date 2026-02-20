# File: urls.py
# Author: Dingwen Yang(laoba@bu.edu), 2/12/2026
# Description: Map MiniInsta URL routes to views.

from django.urls import path
from .views import ShowAllView, ProfileDetailView, PostDetailView, CreatePostView
urlpatterns = [
    path('', ShowAllView.as_view(), name="show_all"),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name="show_profile"),
    path('profile/<int:pk>/create_post', CreatePostView.as_view(), name="create_post"),
    path('post/<int:pk>', PostDetailView.as_view(), name="show_post"),
]
