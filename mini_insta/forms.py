"""
File: forms.py
Author: Dingwen Yang(laoba@bu.edu), 2/20/2026
Description: Define forms for creating MiniInsta posts
"""

from django import forms
from .models import *


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["caption"]


class UpdatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["caption"]


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["display_name", "profile_image_url", "bio_text"]
