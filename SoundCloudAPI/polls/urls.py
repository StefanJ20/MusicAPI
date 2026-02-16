from django.urls import path
from . import views  # type: ignore

urlpatterns = [
    path("", views.index, name="index"),
    path("auth/soundcloud/callback/", views.soundcloud_callback, name="soundcloud_callback"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
]