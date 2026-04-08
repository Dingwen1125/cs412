# File: views.py
# Author: Dingwen Yang(laoba@bu.edu), 4/2/2026
# Description: Define detail views for the dadjokes app, including both HTML views and API views.

import random

from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Joke, Picture
from .serializers import JokeSerializer, PictureSerializer


def _get_random_pair():
    '''generate random joke and picture pair'''
    jokes = list(Joke.objects.all())
    pictures = list(Picture.objects.all())
    return {
        "joke": random.choice(jokes) if jokes else None,
        "picture": random.choice(pictures) if pictures else None
    }


def random_page(request):
    '''render the random page'''
    return render(request, "dadjokes/random.html", _get_random_pair())


def joke_list(request):
    '''render the joke list page'''
    context = {"jokes": Joke.objects.all().order_by("-created_at")}
    return render(request, "dadjokes/joke_list.html", context)


def joke_detail(request, pk):
    '''render the detail page for a joke'''
    joke = get_object_or_404(Joke, pk=pk)
    return render(request, "dadjokes/joke_detail.html", {"joke": joke})


def picture_list(request):
    '''render all the pictures'''
    context = {"pictures": Picture.objects.all().order_by("-created_at")}
    return render(request, "dadjokes/picture_list.html", context)


def picture_detail(request, pk):
    '''render the detail page for a picture'''
    picture = get_object_or_404(Picture, pk=pk)
    return render(request, "dadjokes/picture_detail.html", {"picture": picture})


class RandomJokeAPIView(APIView):
    '''API endpoint to get a random joke'''
    def get(self, request):
        joke = Joke.objects.order_by("?").first()
        if joke is None:
            return Response(
                {"detail": "No jokes available."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(JokeSerializer(joke).data)


class JokeListCreateAPIView(generics.ListCreateAPIView):
    '''API endpoint to list all jokes or create a new joke'''
    queryset = Joke.objects.all().order_by("-created_at")
    serializer_class = JokeSerializer


class JokeDetailAPIView(generics.RetrieveAPIView):
    '''API endpoint to retrieve a joke by its ID'''
    queryset = Joke.objects.all()
    serializer_class = JokeSerializer


class PictureListAPIView(generics.ListAPIView):
    '''API endpoint to list all pictures'''
    queryset = Picture.objects.all().order_by("-created_at")
    serializer_class = PictureSerializer


class PictureDetailAPIView(generics.RetrieveAPIView):
    '''API endpoint to retrieve a picture by its ID'''
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer


class RandomPictureAPIView(APIView):
    '''API endpoint to get a random picture'''
    def get(self, request):
        picture = Picture.objects.order_by("?").first()
        if picture is None:
            return Response(
                {"detail": "No pictures available."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(PictureSerializer(picture).data)
