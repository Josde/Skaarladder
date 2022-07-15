from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('player/<str:player>', views.player, name='player'),
    path('create/', views.create_challenge, name='create_challenge'),
    path('create/htmx/user-form/', views.create_user_form, name='player_form'),
    path('create/htmx/provisional_parse/', views.provisional_parse, name='provisional_parse'),
    path('challenge/<int:id>', views.challenge, name='challenge'),
]