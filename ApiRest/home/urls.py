from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.users_collection),
    path("users/<str:pk>/", views.users_detail),
    path("users/<str:pk>/dossier/", views.dossier_sante),
]
