from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.users_collection),
    path("users/<str:pk>/", views.users_detail),
    path("users/<str:pk>/dossier/", views.dossier_sante),
    path("auth/signup/", views.signup_json),
    path("auth/login/", views.login_json),
    path("auth/logout/", views.logout_json),
    path("auth/me/", views.me_json),
]
