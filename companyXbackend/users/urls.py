from django.urls import path

from users.views import SubmitReviewView, LoginWithOtpAPIView, RegisterUserAPIView

urlpatterns = [
    path("users/register", RegisterUserAPIView.as_view(), name="user-register"),
    path("users/login", LoginWithOtpAPIView.as_view(), name="user-login"),
    path("user/submit_review", SubmitReviewView.as_view(), name="submit-review")
    # TODO: all reviews
    # TODO: all reviews by single user
]
