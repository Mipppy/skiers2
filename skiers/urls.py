from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("rescan", views.rescan, name="rescan"),
    path("racers/<int:id>", views.racer, name="racers"),
    path("tracked_racers", views.tracked_racers, name="tracked")
]

