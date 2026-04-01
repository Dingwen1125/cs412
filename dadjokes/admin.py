from django.contrib import admin

from .models import Joke, Picture


@admin.register(Joke)
class JokeAdmin(admin.ModelAdmin):
    list_display = ("id", "contributor", "created_at")
    search_fields = ("text", "contributor")
    ordering = ("-created_at",)


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ("id", "contributor", "image_url", "created_at")
    search_fields = ("image_url", "contributor")
    ordering = ("-created_at",)
