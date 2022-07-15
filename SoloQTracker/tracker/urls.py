from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('player/<str:player>', views.player, name='player'),
    path('create', views.create_challenge, name='create_challenge'),
    path('challenge/<int:id>', views.challenge, name='challenge')
]