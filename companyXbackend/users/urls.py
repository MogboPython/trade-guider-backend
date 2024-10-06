from django.urls import path

from users.views import LoginWithOtpAPIView, RegisterUserAPIView

urlpatterns = [
    path("users/register", RegisterUserAPIView.as_view(), name="user-register"),
    path("users/login", LoginWithOtpAPIView.as_view(), name="user-login"),
]
