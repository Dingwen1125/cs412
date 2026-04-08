from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Post, Profile
from .serializers import CreatePostSerializer, PostSerializer, ProfileSerializer


class MiniInstaAPIRootView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {
                "profiles": request.build_absolute_uri(reverse("api_profiles")),
                "create_post": request.build_absolute_uri(reverse("api_posts_create")),
            }
        )


class ProfileListAPIView(generics.ListAPIView):
    queryset = Profile.objects.all().order_by("username", "pk")
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]


class ProfileDetailAPIView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]


class ProfilePostsAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        profile = get_object_or_404(Profile, pk=self.kwargs["pk"])
        return profile.get_all_posts()


class ProfileFeedAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        profile = get_object_or_404(Profile, pk=self.kwargs["pk"])
        return profile.get_post_feed()


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = CreatePostSerializer
    permission_classes = [permissions.IsAuthenticated]
