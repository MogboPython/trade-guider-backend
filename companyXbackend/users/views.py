import secrets

from common.helpers import send_email, generate_access_token, generate_refresh_token

from django.core.cache import cache

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User, Review
from .serializers import UserSerializer, LoginWithOTPSerializer

# Create your views here.

class RegisterUserAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        email = serializer.validated_data['email']

        otp = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
        cache.set(f'otp:{email}', otp, timeout=900)  # 15 minutes

        email_subject = f'Use code {otp} to set up your TradeGuider account '
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Verification Code for Your Account</h2>
            <p>Hi,,</p>
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

        send_email(to=email, subject=email_subject, html=email_body)

        return Response(
            data={'success': True, 'message': 'Verification code sent to your email address'},
            status=status.HTTP_200_OK,
        )

class LoginWithOtpAPIView(GenericAPIView):
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
        return Response(
            status=status.HTTP_200_OK,
            data={'success': True, 'data': {'access_token': access_token, 'refresh_token': refresh_token}},
        )

class SubmitReviewView(APIView):
    """Endpoint to create a new book."""
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request, *args, **kwargs):
        file = request.data.get('file')
        if not file:
            return Response({'success': False, 'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        Review.objects.create(
            file=file,
            user=request.user,
        )

        return Response(
            data={'success': True},
            status=status.HTTP_200_OK,
        )

# TODO: get all reviews, authentication not needed

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
