from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('player/<str:player>', views.player, name='player'),
]