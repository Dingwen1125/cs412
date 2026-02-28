# File: urls.py
# Author: Dingwen Yang(laoba@bu.edu), 2/12/2026
# Description: Map MiniInsta URL routes to views.

from django.urls import path
from .views import ShowAllView, ProfileDetailView, ShowFollowersDetailView, ShowFollowingDetailView, PostFeedListView, SearchView, PostDetailView, CreatePostView, UpdateProfileView, DeletePostView, UpdatePostView
urlpatterns = [
    path('', ShowAllView.as_view(), name="show_all"),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name="show_profile"),
    path('profile/<int:pk>/followers', ShowFollowersDetailView.as_view(), name="show_followers"),
    path('profile/<int:pk>/following', ShowFollowingDetailView.as_view(), name="show_following"),
    path('profile/<int:pk>/feed', PostFeedListView.as_view(), name="show_feed"),
    path('profile/<int:pk>/search', SearchView.as_view(), name="search"),
    path('profile/<int:pk>/create_post', CreatePostView.as_view(), name="create_post"),
    path('post/<int:pk>', PostDetailView.as_view(), name="show_post"),
    path('post/<int:pk>/update', UpdatePostView.as_view(), name="update_post"),
    path('profile/<int:pk>/update', UpdateProfileView.as_view(), name="update_profile"),
    path('post/<int:pk>/delete', DeletePostView.as_view(), name="delete_post"),
]
