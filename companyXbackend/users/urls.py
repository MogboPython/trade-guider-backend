from django.urls import path

from users.views import (
    ReviewListView,
    LoginSerializer,
    SubmitReviewView,
    UserReviewListView,
    LoginWithOtpAPIView,
    RegisterUserAPIView,
    ReviewDetailAPIView,
)

urlpatterns = [
    path("users/register", RegisterUserAPIView.as_view(), name="user-register"),
    path("users/get_login_otp", LoginSerializer.as_view(), name="get-user-login-otp"),
    path("users/login", LoginWithOtpAPIView.as_view(), name="user-login"),
    path("users/submit_review", SubmitReviewView.as_view(), name="submit-review"),
    path("users/<str:id>", UserReviewListView.as_view(), name="user-reviews-list"),
    path("reviews", ReviewListView.as_view(), name="reviews-list"),
    path("reviews/<str:id>", ReviewDetailAPIView.as_view(), name='review-detail'),
]
