from django.urls import path
from django.conf import settings
from . import views
from django.conf.urls.static import static
urlpatterns = [ 
    path(r'', views.home_page, name="home"),
    path(r'about', views.about, name="about"),
]+ static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)