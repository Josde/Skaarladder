from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_ladder, name="create_ladder"),
    path("create/htmx/user-form/", views.create_user_form, name="player_form"),
    path(
        "create/htmx/provisional_parse/",
        views.provisional_parse,
        name="provisional_parse",
    ),
    path("ladder/", views.ladder, name="ladder"),
    path("ladder/<int:ladder_id>/", views.ladder, name="ladder"),
    path("ladder_loading/<str:job_id>/", views.ladder_loading, name="ladder_loading"),
    path("htmx/search/", views.search, name="search"),
    path("error/", views.error, name="error"),
]
