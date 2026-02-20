# File: admin.py
# Author: Dingwen Yang(laoba@bu.edu), 2/12/2026
# Description: Register MiniInsta models in Django admin.

from django.contrib import admin

# Register your models here.
from .models import Profile, Post, Photo
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Photo)
