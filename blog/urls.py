from django.urls import path
from .views import ShowAllView
urlpatterns = [
    path('', ShowAllView.as_view(), name="show_all")
]