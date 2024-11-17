from django.urls import path

from users.views import (
    ReviewListView,
    LoginOtpAPIView,
    SubmitReviewView,
    LikeCreateAPIView,
    DeleteReviewAPIView,
    LoginWithOtpAPIView,
    RegisterUserAPIView,
    ReviewDetailAPIView,
    UpdateUserProfileAPIView,
)

urlpatterns = [
    path('users/register', RegisterUserAPIView.as_view(), name='user-register'),
    path('users/profile_update/<str:user_id>', UpdateUserProfileAPIView.as_view(), name='update-profile'),
    path('users/get_login_otp', LoginOtpAPIView.as_view(), name='get-user-login-otp'),
    path('users/login', LoginWithOtpAPIView.as_view(), name='user-login'),
    path('users/submit_review', SubmitReviewView.as_view(), name='submit-review'),
    path('users/<str:user_id>', ReviewListView.as_view(), name='user-reviews-list'),
    path('reviews', ReviewListView.as_view(), name='reviews-list'),
    path('reviews/<str:review_id>', ReviewDetailAPIView.as_view(), name='review-detail'),
    path('reviews/<str:review_id>/like', LikeCreateAPIView.as_view(), name='like-review'),
    path('reviews/<str:review_id>/delete/', DeleteReviewAPIView.as_view(), name='delete-review'),
]
