from django.db.models import Avg

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import AllowAny

from users.models import Review
from common.responses import success_response
from common.pagination import CustomPagination

# from users.serializers import ReviewSerializer
from .models import Company
from .serializers import CompanySerializer, CompanyReviewSerializer, CompanySummarySerializer


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

class GetCompaniesAPIView(ListAPIView):
    """Endpoint to fetch details of multiple Companies."""

    serializer_class = CompanySummarySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Company.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)



class CompanyReviewsListView(ListAPIView):
    """Endpoint to fetch all the reviews of a Company."""

    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = CompanyReviewSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        website = self.kwargs.get('website')
        subcategory = self.request.query_params.getlist('subcategory')

        if website:
            queryset = queryset.filter(company__website=website)
        if subcategory:
            queryset = queryset.filter(company__subcategory=subcategory)

        return queryset

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'subcategory',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='fetch by subcategories',
            ),
        ]
    )

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return success_response({
                "success": True,
                "data": {
                    "company": None,
                    "reviews": []
                }
            })

        company = queryset.first().company
        serializer = self.get_serializer(queryset, many=True)
        data = {
            "company": {
                "company_name": company.company_name,
                "company_website": company.website,
                "is_claimed": company.is_claimed,
                "number_of_reviews": company.number_of_reviews,
                "avg_rating": company.average_rating,
            },
            "reviews": serializer.data
        }

        return success_response(data)
