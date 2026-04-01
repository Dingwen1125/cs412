from rest_framework import serializers

from .models import Joke, Picture


class JokeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Joke
        fields = ["id", "text", "contributor", "created_at"]


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ["id", "image_url", "contributor", "created_at"]
