import random

from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Joke, Picture
from .serializers import JokeSerializer, PictureSerializer


def _get_random_pair():
    jokes = list(Joke.objects.all())
    pictures = list(Picture.objects.all())
    return {
        "joke": random.choice(jokes) if jokes else None,
        "picture": random.choice(pictures) if pictures else None,
    }


def random_page(request):
    return render(request, "dadjokes/random.html", _get_random_pair())


def joke_list(request):
    context = {"jokes": Joke.objects.all().order_by("-created_at")}
    return render(request, "dadjokes/joke_list.html", context)


def joke_detail(request, pk):
    joke = get_object_or_404(Joke, pk=pk)
    return render(request, "dadjokes/joke_detail.html", {"joke": joke})


def picture_list(request):
    context = {"pictures": Picture.objects.all().order_by("-created_at")}
    return render(request, "dadjokes/picture_list.html", context)


def picture_detail(request, pk):
    picture = get_object_or_404(Picture, pk=pk)
    return render(request, "dadjokes/picture_detail.html", {"picture": picture})


class RandomJokeAPIView(APIView):
    def get(self, request):
        joke = Joke.objects.order_by("?").first()
        if joke is None:
            return Response(
                {"detail": "No jokes available."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(JokeSerializer(joke).data)


class JokeListCreateAPIView(generics.ListCreateAPIView):
    queryset = Joke.objects.all().order_by("-created_at")
    serializer_class = JokeSerializer


class JokeDetailAPIView(generics.RetrieveAPIView):
    queryset = Joke.objects.all()
    serializer_class = JokeSerializer


class PictureListAPIView(generics.ListAPIView):
    queryset = Picture.objects.all().order_by("-created_at")
    serializer_class = PictureSerializer


class PictureDetailAPIView(generics.RetrieveAPIView):
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer


class RandomPictureAPIView(APIView):
    def get(self, request):
        picture = Picture.objects.order_by("?").first()
        if picture is None:
            return Response(
                {"detail": "No pictures available."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(PictureSerializer(picture).data)
