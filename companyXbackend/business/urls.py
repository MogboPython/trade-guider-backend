from django.urls import path

from .views import RegisterCompanyAPIView

urlpatterns = [
    path("company/register", RegisterCompanyAPIView.as_view(), name="company-register")
]
