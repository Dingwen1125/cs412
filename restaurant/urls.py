from django.urls import path
from django.conf import settings
from . import views
from django.conf.urls.static import static

app_name = "restaurant"
urlpatterns =[
    path(r'', views.home, name = 'home'),
    path(r'order', views.order, name = 'order'),
    path(r'submit', views.submit, name = 'submit'),
]