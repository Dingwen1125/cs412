# File: api_views.py
# Author: Dingwen Yang(laoba@bu.edu), 4/9/2026
# Description: The API views for the mini_insta app.
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from .models import Post, Profile
from .serializers import CreatePostSerializer, PostSerializer, ProfileSerializer


class RequestTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        '''authentication using token from request data'''
        auth_result = super().authenticate(request)
        if auth_result is not None:
            return auth_result

        token_key = request.query_params.get("token") or request.data.get("token")
        if not token_key:
            return None

        return self.authenticate_credentials(token_key)


class MiniInstaAPIRootView(APIView):
    '''API root view that provides links to all available API endpoints.'''
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {
                "login": request.build_absolute_uri(reverse("api_login")),
                "profiles": request.build_absolute_uri(reverse("api_profiles")),
                "create_post": request.build_absolute_uri(reverse("api_posts_create")),
            }
        )


class APILoginView(APIView):
    '''API view for user login that returns an authentication token'''
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        '''Authenticate user and return the token with user and profile info'''
        username = request.data.get("username", "")
        password = request.data.get("password", "")

        if not username or not password:
            return Response(
                {"error": "Both username and password are required."},
                status=HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request=request, username=username, password=password)
        if user is None:
            return Response(
                {"error": "Invalid username or password."},
                status=HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)
        profile = Profile.objects.filter(user=user).order_by("pk").first()
        if profile is None:
            return Response(
                {"error": "This account does not have a MiniInsta profile."},
                status=HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
                "profile_id": profile.pk,
            },
            status=HTTP_200_OK,
        )


class ProfileListAPIView(generics.ListAPIView):
    '''API view to list all profiles'''
    queryset = Profile.objects.all().order_by("username", "pk")
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]


class ProfileDetailAPIView(generics.RetrieveAPIView):
    '''API view to retrieve details of a specific profile'''
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]


class ProfilePostsAPIView(generics.ListAPIView):
    '''API view to list all posts of a specific profile'''
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        profile = get_object_or_404(Profile, pk=self.kwargs["pk"])
        return profile.get_all_posts()


class ProfileFeedAPIView(generics.ListAPIView):
    '''API view to list the post feed of a specific profile'''
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        profile = get_object_or_404(Profile, pk=self.kwargs["pk"])
        return profile.get_post_feed()


class PostCreateAPIView(generics.CreateAPIView):
    '''API view to create a new post'''
    serializer_class = CreatePostSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [RequestTokenAuthentication, TokenAuthentication, SessionAuthentication]
