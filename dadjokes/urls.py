from django.urls import path

from . import views

urlpatterns = [
    path("", views.random_page, name="dadjokes_home"),
    path("random", views.random_page, name="dadjokes_random"),
    path("jokes", views.joke_list, name="dadjokes_jokes"),
    path("joke/<int:pk>", views.joke_detail, name="dadjokes_joke_detail"),
    path("pictures", views.picture_list, name="dadjokes_pictures"),
    path("picture/<int:pk>", views.picture_detail, name="dadjokes_picture_detail"),
    path("api/", views.RandomJokeAPIView.as_view(), name="dadjokes_api_root"),
    path("api/random", views.RandomJokeAPIView.as_view(), name="dadjokes_api_random"),
    path("api/jokes", views.JokeListCreateAPIView.as_view(), name="dadjokes_api_jokes"),
    path("api/joke/<int:pk>", views.JokeDetailAPIView.as_view(), name="dadjokes_api_joke_detail"),
    path("api/pictures", views.PictureListAPIView.as_view(), name="dadjokes_api_pictures"),
    path("api/picture/<int:pk>", views.PictureDetailAPIView.as_view(), name="dadjokes_api_picture_detail"),
    path("api/random_picture", views.RandomPictureAPIView.as_view(), name="dadjokes_api_random_picture"),
]
