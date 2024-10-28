import secrets

from django.shortcuts import get_object_or_404
from django.core.cache import cache

from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated

from common.helpers import send_email, generate_access_token, generate_refresh_token
from common.responses import success_response
from common.pagination import CustomPagination
from common.authentication import IsOwnerOnly

from .models import User, Review
from .serializers import UserSerializer, LoginSerializer, ReviewSerializer, LoginWithOTPSerializer


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

        send_email(to=email, subject=email_subject, html=email_body)
        serializer = self.get_serializer(user)
        response_data = serializer.data

        # TODO: remove, leave only for testing
        data = {'message': 'Verification code sent to your email address', 'data': response_data, 'code': otp}
        return success_response(data, status.HTTP_200_OK)


# TODO: login route that returns otp
class LoginOtpAPIView(GenericAPIView):
    """Endpoint to get login otp for a user."""

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        otp = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
        cache.set(f'otp:{email}', otp, timeout=900)

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

        # TODO: remove, leave only for testing
        data = {'message': 'Login code sent to your email address', 'email': email, 'code': otp}
        return success_response(data, status.HTTP_200_OK)


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

        return Response(
            status=status.HTTP_200_OK,
            data={
                'success': True,
                'data': {'access_token': access_token, 'refresh_token': refresh_token, 'user': response_data},
            },
        )


class UpdateUserProfileAPIView(UpdateAPIView):
    """Endpoint to update user detail"""

    permission_classes = [IsAuthenticated, IsOwnerOnly]
    serializer_class = UserSerializer

    def get_object(self):
        user = self.request.user
        user_id = self.kwargs.get('user_id')

        if user_id and str(user.id) != str(user_id):
            msg = "You don't have permission to update this profile."
            raise PermissionDenied(msg)

        return user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_data = {
            'message': 'Profile updated successfully',
            'data': serializer.data
        }
        return success_response(response_data, status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


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

class ReviewListView(ListAPIView):
    """Endpoint to fetch all reviews by a User."""

    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.kwargs.get('id')
        if user_id:
            queryset = queryset.filter(user__id=user_id)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return success_response(serializer.data)


class ReviewDetailAPIView(ListAPIView):
    """Endpoint to fetch details of a single review."""

    lookup_field = 'id'
    serializer_class = ReviewSerializer
    queryset = Review.objects.get_queryset()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        return success_response(data)

class DeleteReviewAPIView(DestroyAPIView):
    """Endpoint to delete a review."""

    permission_classes = [IsAuthenticated, IsOwnerOnly]
    queryset = Review.objects.all()

    def get_object(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )

        if review.user != self.request.user:
            msg = "You don't have permission to delete this review."
            raise PermissionDenied(msg)

        return review

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        response_data = {
            'message': 'Review deleted successfully'
        }
        return success_response(response_data, status.HTTP_200_OK)

# TODO: get all reviews by single user for themselves, authentication needed, delete review? ******
# TODO: Route to update profile

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
