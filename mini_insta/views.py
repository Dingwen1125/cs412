# File: views.py
# Author: Dingwen Yang(laoba@bu.edu), 2/12/2026
# Description: Define list/detail views for MiniInsta profiles.

from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView
from .forms import CreatePostForm
from .models import Profile, Post, Photo
# Create your views here.

class ShowAllView(ListView):
    '''
    show all the item in the Profile
    '''
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"

class ProfileDetailView(DetailView):
    '''
    show one item in Profile
    '''
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # dispaly this image when a post has no photos.
        context["default_photo_url"] = "https://upload.wikimedia.org/wikipedia/commons/a/a3/Image-not-found.png"
        return context


class PostDetailView(DetailView):
    '''
    show one item in Post
    '''
    model = Post
    template_name = "mini_insta/show_post.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        # provide fallback image URL for posts without photos
        context = super().get_context_data(**kwargs)
        context["default_photo_url"] = "https://upload.wikimedia.org/wikipedia/commons/a/a3/Image-not-found.png"
        return context


class CreatePostView(CreateView):
    '''
    create one Post for a given Profile
    '''
    template_name = "mini_insta/create_post_form.html"
    form_class = CreatePostForm

    def get_context_data(self, **kwargs):
        # add target profile from URL
        context = super().get_context_data(**kwargs)
        context["profile"] = Profile.objects.get(pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        # attach profile before saving post
        profile = Profile.objects.get(pk=self.kwargs["pk"])
        form.instance.profile = profile
        response = super().form_valid(form)
        image_url = self.request.POST.get("image_url", "").strip()
        if image_url:
            Photo.objects.create(post=self.object, image_url=image_url)
        return response

    def get_success_url(self):
        # redirect to the new post just created detail page
        return reverse("show_post", kwargs={"pk": self.object.pk})
