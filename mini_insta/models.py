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

    def get_all_posts(self):
        return Post.objects.filter(profile=self).order_by("-timestamp")

    def __str__(self):
        return f'{self.username}'


class Post(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    caption = models.TextField(blank=True)

    def get_all_photos(self):
        return Photo.objects.filter(post=self).order_by("-timestamp")

    def __str__(self):
        return f'Post by {self.profile.username} at {self.timestamp}'


class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image_url = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Photo for post {self.post.id} at {self.timestamp}'
