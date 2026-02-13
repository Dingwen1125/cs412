# File: admin.py
# Author: Dingwen Yang(laoba@bu.edu), 2/12/2026
# Description: Register MiniInsta models in Django admin.

from django.contrib import admin

# Register your models here.
from .models import Profile
admin.site.register(Profile)