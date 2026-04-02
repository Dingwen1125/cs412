# File: models.py
# Author: Dingwen Yang(laoba@bu.edu), 4/2/2026
# Description: Define the dadjokes' data model.

from django.db import models


class Joke(models.Model):
    text = models.TextField()
    contributor = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Joke #{self.pk} by {self.contributor}"


class Picture(models.Model):
    image_url = models.URLField(max_length=500)
    contributor = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Picture #{self.pk} by {self.contributor}"
