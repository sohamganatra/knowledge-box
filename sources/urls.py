from django.urls import path

from . import views

urlpatterns = [
    path('list_sources', views.list_sources, name='list_sources'),
]
