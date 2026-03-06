# File: urls.py
# Author: Dingwen Yang(laoba@bu.edu), 2/12/2026
# Description: Map MiniInsta URL routes to views.

from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .views import ShowAllView, CreateProfileView, ProfileDetailView, MyProfileDetailView, ShowFollowersDetailView, ShowFollowingDetailView, PostFeedListView, SearchView, PostDetailView, CreatePostView, UpdateProfileView, DeletePostView, UpdatePostView, FollowProfileView, DeleteFollowProfileView, LikePostView, DeleteLikePostView
urlpatterns = [
    path('', ShowAllView.as_view(), name="show_all"),
    path('create_profile', CreateProfileView.as_view(), name="create_profile"),
    path('profile', MyProfileDetailView.as_view(), name="show_my_profile"),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name="show_profile"),
    path('profile/<int:pk>/followers', ShowFollowersDetailView.as_view(), name="show_followers"),
    path('profile/<int:pk>/following', ShowFollowingDetailView.as_view(), name="show_following"),
    path('profile/<int:pk>/follow', FollowProfileView.as_view(), name="follow_profile"),
    path('profile/<int:pk>/delete_follow', DeleteFollowProfileView.as_view(), name="delete_follow_profile"),
    path('profile/feed', PostFeedListView.as_view(), name="show_feed"),
    path('profile/search', SearchView.as_view(), name="search"),
    path('profile/create_post', CreatePostView.as_view(), name="create_post"),
    path('post/<int:pk>', PostDetailView.as_view(), name="show_post"),
    path('post/<int:pk>/like', LikePostView.as_view(), name="like_post"),
    path('post/<int:pk>/delete_like', DeleteLikePostView.as_view(), name="delete_like_post"),
    path('post/<int:pk>/update', UpdatePostView.as_view(), name="update_post"),
    path('profile/update', UpdateProfileView.as_view(), name="update_profile"),
    path('post/<int:pk>/delete', DeletePostView.as_view(), name="delete_post"),
    path('login/', auth_views.LoginView.as_view(template_name='mini_insta/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='logout_confirmation'), name='logout'),
    path('logout_confirmation/', TemplateView.as_view(template_name='mini_insta/logged_out.html'), name='logout_confirmation'),
]
