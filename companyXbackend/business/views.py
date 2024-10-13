from common.responses import success_response

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny

from .serializers import CompanySerializer

# Create your views here.


class RegisterCompanyAPIView(GenericAPIView):
    """Endpoint to register a new user."""

    permission_classes = [AllowAny]
    serializer_class = CompanySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = serializer.save()

        response_serializer = self.get_serializer(company)

        return success_response(response_serializer.data, status.HTTP_200_OK)
