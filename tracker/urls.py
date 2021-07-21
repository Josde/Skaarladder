from django.urls import path

from . import views
from .views import LeagueDataListView

urlpatterns = [
    path('', views.index, name='index'),
    path('tracker/', LeagueDataListView.as_view(), name='tracker'),
    path('error/', views.error, name='error')
]
