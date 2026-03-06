# File: views.py
# Author: Dingwen Yang(laoba@bu.edu), 2/12/2026
# Description: Define list/detail views for MiniInsta profiles.

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import CreatePostForm, UpdatePostForm, UpdateProfileForm, CreateProfileForm
from .models import Profile, Post, Photo, Follow, Like
# Create your views here.


class MiniInstaLoginRequiredMixin(LoginRequiredMixin):
    def get_login_url(self):
        return "/mini_insta/login/"

    def get_logged_in_profile(self):
        """Return the Profile linked to the authenticated user"""
        if not self.request.user.is_authenticated:
            return None
        return Profile.objects.filter(user=self.request.user).order_by("pk").first()

    def get_required_logged_in_profile(self):
        """Return logged-in user's Profile or reject access if missing."""
        profile = self.get_logged_in_profile()
        if profile is None:
            raise PermissionDenied
        return profile

    def user_owns_profile(self, profile):
        """Return True when authenticated user owns the given profile."""
        return self.request.user.is_authenticated and profile.user_id == self.request.user.id

    def require_profile_owner(self, profile):
        """Allow access only to the owner of this profile."""
        if not self.user_owns_profile(profile):
            raise PermissionDenied

    def redirect_to_next_or(self, fallback_url):
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
            return redirect(next_url)
        return redirect(fallback_url)

class ShowAllView(ListView):
    '''
    show all the item in the Profile
    '''
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"


class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = "mini_insta/create_profile_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_creation_form"] = kwargs.get("user_creation_form", UserCreationForm())
        return context

    def form_valid(self, form):
        user_creation_form = UserCreationForm(self.request.POST)
        if not user_creation_form.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, user_creation_form=user_creation_form)
            )
        user = user_creation_form.save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        form.instance.user = user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("show_my_profile")


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
        logged_in_profile = None
        if self.request.user.is_authenticated:
            logged_in_profile = Profile.objects.filter(user=self.request.user).order_by("pk").first()
        profile = self.object
        context["logged_in_profile"] = logged_in_profile
        context["can_follow"] = bool(logged_in_profile and logged_in_profile.pk != profile.pk)
        context["is_following"] = bool(logged_in_profile and Follow.objects.filter(profile=profile,follower_profile=logged_in_profile,).exists())
        context["default_photo_url"] = "https://upload.wikimedia.org/wikipedia/commons/a/a3/Image-not-found.png"
        return context


class MyProfileDetailView(MiniInstaLoginRequiredMixin, DetailView):
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return self.get_required_logged_in_profile()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["logged_in_profile"] = self.object
        context["can_follow"] = False
        context["is_following"] = False
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


class PostFeedListView(MiniInstaLoginRequiredMixin, ListView):
    model = Post
    template_name = "mini_insta/show_feed.html"
    context_object_name = "posts"

    def get_profile(self):
        if not hasattr(self, "_profile"):
            self._profile = self.get_required_logged_in_profile()
        return self._profile

    def get_queryset(self):
        """Return feed posts for the logged-in user's profile."""
        return self.get_profile().get_post_feed()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.get_profile()
        context["default_photo_url"] = "https://upload.wikimedia.org/wikipedia/commons/a/a3/Image-not-found.png"
        return context


class SearchView(MiniInstaLoginRequiredMixin, ListView):
    model = Post
    template_name = "mini_insta/search_results.html"
    context_object_name = "post_results"

    def get_profile(self):
        """Load and cache logged-in user's profile."""
        if not hasattr(self, "_profile"):
            self._profile = self.get_required_logged_in_profile()
        return self._profile

    def dispatch(self, request, *args, **kwargs):
        """Show search form when no query is provided"""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        query = request.GET.get("query", "").strip()
        if not query:
            return render(
                request,
                "mini_insta/search.html",
                {"profile": self.get_profile()},
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return posts whose caption contains the searched query text"""
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
        logged_in_profile = None
        if self.request.user.is_authenticated:
            logged_in_profile = Profile.objects.filter(user=self.request.user).order_by("pk").first()
        post = self.object
        context["can_like"] = bool(logged_in_profile and post.profile_id != logged_in_profile.pk)
        context["has_liked"] = bool(
            logged_in_profile and Like.objects.filter(post=post,profile=logged_in_profile,).exists())
        context["default_photo_url"] = "https://upload.wikimedia.org/wikipedia/commons/a/a3/Image-not-found.png"
        return context


class CreatePostView(MiniInstaLoginRequiredMixin, CreateView):
    '''
    create one Post for a given Profile
    '''
    template_name = "mini_insta/create_post_form.html"
    form_class = CreatePostForm

    def get_profile(self):
        if not hasattr(self, "_profile"):
            self._profile = self.get_required_logged_in_profile()
        return self._profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.get_profile()
        return context

    def form_valid(self, form):
        """Attach profile to post and create Photo rows for uploaded files."""
        form.instance.profile = self.get_profile()
        response = super().form_valid(form)
        image_files = self.request.FILES.getlist("image_files")
        for image_file in image_files:
            Photo.objects.create(post=self.object, image_file=image_file)
        return response

    def get_success_url(self):
        return reverse("show_post", kwargs={"pk": self.object.pk})


class UpdateProfileView(MiniInstaLoginRequiredMixin, UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_insta/update_profile_form.html"

    def get_object(self, queryset=None):
        return self.get_required_logged_in_profile()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.object
        return context

    def get_success_url(self):
        return reverse("show_my_profile")


class DeletePostView(MiniInstaLoginRequiredMixin, DeleteView):
    model = Post
    template_name = "mini_insta/delete_post_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.object = self.get_object()
        self.require_profile_owner(self.object.profile)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = self.object
        context["profile"] = self.object.profile
        return context

    def get_success_url(self):
        return reverse("show_my_profile")


class UpdatePostView(MiniInstaLoginRequiredMixin, UpdateView):
    model = Post
    form_class = UpdatePostForm
    template_name = "mini_insta/update_post_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.object = self.get_object()
        self.require_profile_owner(self.object.profile)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = self.object
        context["profile"] = self.object.profile
        return context

    def get_success_url(self):
        return reverse("show_post", kwargs={"pk": self.object.pk})


class FollowProfileView(MiniInstaLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        logged_in_profile = self.get_required_logged_in_profile()
        target_profile = get_object_or_404(Profile, pk=self.kwargs["pk"])
        if target_profile.pk != logged_in_profile.pk:
            Follow.objects.get_or_create(
                profile=target_profile,
                follower_profile=logged_in_profile,
            )
        return self.redirect_to_next_or(reverse("show_profile", kwargs={"pk": target_profile.pk}))


class DeleteFollowProfileView(MiniInstaLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        logged_in_profile = self.get_required_logged_in_profile()
        target_profile = get_object_or_404(Profile, pk=self.kwargs["pk"])
        Follow.objects.filter(
            profile=target_profile,
            follower_profile=logged_in_profile,
        ).delete()
        return self.redirect_to_next_or(reverse("show_profile", kwargs={"pk": target_profile.pk}))


class LikePostView(MiniInstaLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        logged_in_profile = self.get_required_logged_in_profile()
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        if post.profile_id != logged_in_profile.pk:
            Like.objects.get_or_create(
                post=post,
                profile=logged_in_profile,
            )
        return self.redirect_to_next_or(reverse("show_post", kwargs={"pk": post.pk}))


class DeleteLikePostView(MiniInstaLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        logged_in_profile = self.get_required_logged_in_profile()
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        Like.objects.filter(
            post=post,
            profile=logged_in_profile,
        ).delete()
        return self.redirect_to_next_or(reverse("show_post", kwargs={"pk": post.pk}))
