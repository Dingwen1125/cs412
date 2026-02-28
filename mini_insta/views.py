# File: views.py
# Author: Dingwen Yang(laoba@bu.edu), 2/12/2026
# Description: Define list/detail views for MiniInsta profiles.

from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import CreatePostForm, UpdatePostForm, UpdateProfileForm
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
        """Add a fallback image URL for posts that do not have photos."""
        context = super().get_context_data(**kwargs)
        context["default_photo_url"] = "https://upload.wikimedia.org/wikipedia/commons/a/a3/Image-not-found.png"
        return context


class ShowFollowersDetailView(DetailView):
    model = Profile
    template_name = "mini_insta/show_followers.html"
    context_object_name = "profile"


class ShowFollowingDetailView(DetailView):
    model = Profile
    template_name = "mini_insta/show_following.html"
    context_object_name = "profile"


class PostFeedListView(ListView):
    model = Post
    template_name = "mini_insta/show_feed.html"
    context_object_name = "posts"

    def get_queryset(self):
        """Return the feed posts for the profile identified by URL pk."""
        self.profile = Profile.objects.get(pk=self.kwargs["pk"])
        return self.profile.get_post_feed()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        context["default_photo_url"] = "https://upload.wikimedia.org/wikipedia/commons/a/a3/Image-not-found.png"
        return context


class SearchView(ListView):
    model = Post
    template_name = "mini_insta/search_results.html"
    context_object_name = "post_results"

    def get_profile(self):
        """Load and cache the profile that owns this search request."""
        if not hasattr(self, "_profile"):
            self._profile = Profile.objects.get(pk=self.kwargs["pk"])
        return self._profile

    def dispatch(self, request, *args, **kwargs):
        """Show search form when no query is provided, else run ListView flow."""
        query = request.GET.get("query", "").strip()
        if not query:
            return render(
                request,
                "mini_insta/search.html",
                {"profile": self.get_profile()},
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return posts whose caption contains the search query text."""
        query = self.request.GET.get("query", "").strip()
        if not query:
            return Post.objects.none()
        return Post.objects.filter(
            Q(caption__icontains=query)
        ).order_by("-timestamp")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("query", "").strip()
        profile_results = Profile.objects.none()
        if query:
            profile_results = Profile.objects.filter(
                Q(username__icontains=query) | Q(display_name__icontains=query) |
                Q(bio_text__icontains=query)
            )
        context["profile"] = self.get_profile()
        context["query"] = query
        context["post_results"] = self.get_queryset()
        context["profile_results"] = profile_results
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
        """Add a fallback image URL for posts without photos."""
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
        context = super().get_context_data(**kwargs)
        context["profile"] = Profile.objects.get(pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        """Attach profile to post and create Photo rows for uploaded files."""
        profile = Profile.objects.get(pk=self.kwargs["pk"])
        form.instance.profile = profile
        response = super().form_valid(form)
        image_files = self.request.FILES.getlist("image_files")
        for image_file in image_files:
            Photo.objects.create(post=self.object, image_file=image_file)
        return response

    def get_success_url(self):
        return reverse("show_post", kwargs={"pk": self.object.pk})


class UpdateProfileView(UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_insta/update_profile_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.object
        return context


class DeletePostView(DeleteView):
    model = Post
    template_name = "mini_insta/delete_post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = self.object
        context["profile"] = self.object.profile
        return context

    def get_success_url(self):
        return reverse("show_profile", kwargs={"pk": self.object.profile.pk})


class UpdatePostView(UpdateView):
    model = Post
    form_class = UpdatePostForm
    template_name = "mini_insta/update_post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = self.object
        context["profile"] = self.object.profile
        return context

    def get_success_url(self):
        return reverse("show_post", kwargs={"pk": self.object.pk})
