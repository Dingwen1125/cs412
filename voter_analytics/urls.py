# File: urls.py
# Author: Dingwen Yang (laoba@bu.edu), 3/19/2026
# Description: URL patterns for the voter list, graph page,
# and voter detail page.

from django.urls import path
from . import views 

urlpatterns = [
    path('', views.VotersListView.as_view(), name='home'),
    path('graphs', views.GraphsListView.as_view(), name='graphs'),
    path('voter/<int:pk>', views.VoterDetailView.as_view(), name='voter'),
]
