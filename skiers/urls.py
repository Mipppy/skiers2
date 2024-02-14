from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("rescan", views.rescan, name="rescan"),
    path("racers/<int:id>", views.racer, name="racers"),
    path("tracked_racers", views.tracked_racers, name="tracked"),
    path("search", views.search, name="search"),
    path("teams/<str:name>", views.teams, name="teams"),
    path("all_teams", views.all_teams, name="all_teams")
]

