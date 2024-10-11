import secrets

from common.helpers import send_email, generate_access_token, generate_refresh_token
from common.responses import success_response

from django.core.cache import cache

from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, GenericAPIView
from rest_framework.response import Response

# Create your views here.
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User, Review
from .serializers import UserSerializer, LoginSerializer, ReviewSerializer, LoginWithOTPSerializer


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

class RegisterUserAPIView(GenericAPIView):
    """Endpoint to register a new user."""
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        email = serializer.validated_data['email']

        otp = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
        cache.set(f'otp:{email}', otp, timeout=900)  # 15 minutes

        email_subject = f'Use code {otp} to set up your TradeGuider account '
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Verification Code for Your Account</h2>
            <p>Hi,</p>
            <p>Thanks for signing up with TradeGuider!.</p>
            <p> Here's your code to finish setting up your account:</p>
            <h1 style="font-size: 32px; background-color: #f0f0f0; padding: 10px; text-align: center; letter-spacing: 5px;">{otp}</h1>
            <p>This code will expire in 15 minutes.</p>
            <p><strong>Important:</strong> If you didn't request this code, please ignore this email. Your account security is important to us.</p>
            <p>Thank you for using our service.</p>
            <p>Best regards,<br>Your Support Team</p>
        </body>
        </html>
        """  # noqa: E501

        # TODO: don't forget
        # send_email(to=email, subject=email_subject, html=email_body)
        # serializer = self.get_serializer(user)
        # data = serializer.data
        # return success_response(data, status.HTTP_200_OK)

        return Response(
            # TODO: remove, leave only for testing
            data={'success': True, 'message': 'Verification code sent to your email address', 'code' : otp},
            status=status.HTTP_200_OK,
        )

# TODO: login route that returns otp
class LoginOtpAPIView(GenericAPIView):
    """Endpoint to get login otp for a user."""
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        otp = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
        cache.set(f'otp:{email}', otp, timeout=900)  # 15 minutes

        email_subject = f'Use code {otp} to login to your TradeGuider account '
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Login Code for Your Account</h2>
            <p>Hi,</p>
            <p> Here's your code to log into your account:</p>
            <h1 style="font-size: 32px; background-color: #f0f0f0; padding: 10px; text-align: center; letter-spacing: 5px;">{otp}</h1>
            <p>This code will expire in 15 minutes.</p>
            <p><strong>Important:</strong> If you didn't request this code, please ignore this email. Your account security is important to us.</p>
            <p>Thank you for using our service.</p>
            <p>Best regards,<br>Your Support Team</p>
        </body>
        </html>
        """  # noqa: E501

        send_email(to=email, subject=email_subject, html=email_body)

        return Response(
            # TODO: remove, leave only for testing
            data={'success': True, 'message': 'Login code sent to your email address', 'email': email, 'code' : otp},
            status=status.HTTP_200_OK,
        )


class LoginWithOtpAPIView(GenericAPIView):
    """Endpoint to login a user."""
    serializer_class = LoginWithOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        cached_otp = cache.get(f'otp:{email}', default=None)
        if cached_otp is None:
            return Response(data={'success': False, 'error': 'invalid otp'}, status=status.HTTP_400_BAD_REQUEST)

        if cached_otp != otp:
            return Response(data={'success': False, 'error': 'invalid otp'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(data={'success': False, 'error': 'invalid otp'}, status=status.HTTP_400_BAD_REQUEST)

        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        response_data = UserSerializer(instance=user).data

        cache.delete(f'otp:{email}')
        return Response(
            status=status.HTTP_200_OK,
            data={'success': True, 'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': response_data
            }},
        )

class SubmitReviewView(CreateAPIView):
    """Endpoint to create a new review."""
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = serializer.save()
        response_serializer = self.get_serializer(review)

        return Response(
            data={'success': True, 'data': response_serializer.data},
            status=status.HTTP_200_OK,
        )

class UserReviewListView(ListAPIView):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user__id=user_id)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return success_response(serializer.data)

class ReviewDetailAPIView(ListAPIView):
    lookup_field = 'id'
    serializer_class = ReviewSerializer
    queryset = Review.objects.get_queryset()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        return success_response(data)

# TODO: get all reviews, authentication not needed, single review view
# TODO: get all reviews by single user for themselves, authentication needed ******
# TODO: get all reviews by single user, authentication not needed
# TODO: Swagger ui

# class UserAuthenticationAPIView(GenericAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = AdminLoginSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         auth_service = init_authentication_service()
#         response = auth_service.Authenticate(
#             AuthenticateRequest(
#                 email=serializer.validated_data['email'],
#                 password=serializer.validated_data['password'],
#             )
#         )

#         return success_response(
#             data={
#                 'access_token': response.access_token,
#                 'user': {
#                     'id': response.user.id,
#                     'email': response.user.email,
#                     'first_name': response.user.first_name,
#                     'last_name': response.user.last_name,
#                     'is_admin': True,
#                 },
#             },
#             status_code=status.HTTP_200_OK,
#         )
