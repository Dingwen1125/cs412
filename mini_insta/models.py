# File: models.py
# Author: Dingwen Yang(laoba@bu.edu), 2/12/2026
# Description: Define the MiniInsta profile data model.

from django.db import models
from django.urls import reverse

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

    def get_absolute_url(self):
        return reverse("show_profile", kwargs={"pk": self.pk})

    def get_followers(self):
        '''get all followers account'''
        follows = Follow.objects.filter(profile=self)
        return [follow.follower_profile for follow in follows]

    def get_num_followers(self):
        '''get number of followers'''
        return len(self.get_followers())

    def get_following(self):
        '''get all following accounts'''
        follows = Follow.objects.filter(follower_profile=self)
        return [follow.profile for follow in follows]

    def get_num_following(self):
        '''get number of following accounts'''
        return len(self.get_following())

    def get_post_feed(self):
        '''get post feed'''
        following_ids = Follow.objects.filter(follower_profile=self).values_list("profile_id", flat=True)
        return Post.objects.filter(profile_id__in=following_ids).order_by("-timestamp")



class Post(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    caption = models.TextField(blank=True)

    def get_all_photos(self):
        return Photo.objects.filter(post=self).order_by("-timestamp")

    def get_all_comments(self):
        return Comment.objects.filter(post=self).order_by("timestamp")

    def get_likes(self):
        return Like.objects.filter(post=self).order_by("-timestamp")

    def __str__(self):
        return f'Post by {self.profile.username} at {self.timestamp}'


class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image_url = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    image_file = models.ImageField(blank=True)

    def __str__(self):
        if self.image_url:
            image_ref = self.image_url
        elif self.image_file:
            image_ref = self.image_file.name
        else:
            image_ref = "no-image"
        return f'Photo for post {self.post.id}: {image_ref}'
    
    def get_image_url(self):
        if self.image_url:
            return self.image_url
        if self.image_file:
            return self.image_file.url
        return ""


class Follow(models.Model):
    profile = models.ForeignKey(Profile, related_name="profile", on_delete=models.CASCADE)
    follower_profile = models.ForeignKey(Profile, related_name="follower_profile", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower_profile.username} follow {self.profile.username}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)

    def __str__(self):
        return f"{self.profile.username} commented on {self.post.id}: {self.text[:30]}"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.username} liked post {self.post.id}"
