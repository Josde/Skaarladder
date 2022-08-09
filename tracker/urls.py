from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_challenge, name="create_challenge"),
    path("create/htmx/user-form/", views.create_user_form, name="player_form"),
    path(
        "create/htmx/provisional_parse/",
        views.provisional_parse,
        name="provisional_parse",
    ),
    path("challenge/", views.challenge, name="challenge"),
    path("challenge/<int:challenge_id>/", views.challenge, name="challenge"),
    path("challenge_loading/<str:job_id>/", views.challenge_loading, name="challenge_loading"),
    path("htmx/search/", views.search, name="search"),
    path("error/", views.error, name="error"),
]
