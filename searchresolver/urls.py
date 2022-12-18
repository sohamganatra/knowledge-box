from django.urls import path

from . import views

urlpatterns = [
    path('answer', views.get_answer, name='get_answer'),
]
