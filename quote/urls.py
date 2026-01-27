# File: urls.py
# Author: Dingwen Yang(laoba@bu.edu), 1/27/2026
# Description: pathes for the differrent pages quote app
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path(r'', views.home_page, name="home"),
    path(r'quoteOf', views.quoteOf, name="quoteOf"),
    path(r'show_all', views.show_all, name="show_all"),
    path(r'about', views.about, name="about"),

    """the static file path"""
    ] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)