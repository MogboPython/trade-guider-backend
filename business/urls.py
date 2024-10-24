from django.urls import path

from .views import (
    GetCompaniesAPIView,
    CompanyReviewsListView,
    RegisterCompanyAPIView,
)

urlpatterns = [
    path('company/register', RegisterCompanyAPIView.as_view(), name='company-register'),
    path('companies', GetCompaniesAPIView.as_view(), name='get-comapnies'),
    path('review/<str:website>', CompanyReviewsListView.as_view(), name='company-reviews'),
    # TODO: route to update company data
]
