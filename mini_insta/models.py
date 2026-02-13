# File: models.py
# Author: Dingwen Yang(laoba@bu.edu), 2/12/2026
# Description: Define the MiniInsta profile data model.

from django.db import models

# Create your models here.
class Profile(models.Model):
    username = models.TextField(blank=True)
    display_name = models.TextField(blank=True)
    profile_image_url = models.URLField(blank=True)
    bio_text = models.TextField(blank=True)
    join_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.username}'