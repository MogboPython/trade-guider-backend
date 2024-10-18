from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import AllowAny

from users.models import Review
from common.responses import success_response
from common.pagination import CustomPagination

# from users.serializers import ReviewSerializer
from .serializers import ReviewSerializer, CompanySerializer


class RegisterCompanyAPIView(GenericAPIView):
    """Endpoint to register a new company."""

    permission_classes = [AllowAny]
    serializer_class = CompanySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = serializer.save()

        response_serializer = self.get_serializer(company)

        return success_response(response_serializer.data, status.HTTP_200_OK)

class CompanyReviewsListView(ListAPIView):
    """Endpoint to fetch all the reviews of a Company."""

    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        website = self.kwargs.get('website')
        if website:
            queryset = queryset.filter(company__website=website)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # data = {}

        return success_response(serializer.data)
