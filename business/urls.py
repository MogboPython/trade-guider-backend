from django.urls import path

from .views import CompanyReviewsListView, RegisterCompanyAPIView

urlpatterns = [
    path('company/register', RegisterCompanyAPIView.as_view(), name='company-register'),
    path('review/<str:website>', CompanyReviewsListView.as_view(), name='company-reviews'),
    # TODO: route to update company data
]
