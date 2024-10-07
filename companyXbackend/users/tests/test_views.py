import secrets
from unittest.mock import patch

from common.helpers import generate_access_token
from business.models import Company

from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APIClient

from users.models import User, Review


class UserAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('users.views.send_email')
    def test_register_user(self, mock_send_email):
        user_data = {
            'email':"tester@gmail.com",
            'name':'Harper Lee',
            'country':'China',
            'language':'Chinese',
        }

        response = self.client.post(reverse('user-register'), user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Verification code sent to your email address')

        self.assertTrue(User.objects.filter(email='tester@gmail.com').exists())
        self.assertIsNotNone(cache.get('otp:tester@gmail.com'))
        mock_send_email.assert_called_once()

    @patch('users.views.send_email')
    def test_register_user_invalid_data(self, mock_send_email):
        user_data = {
            'email':"invalid_email",
            'name':'Harper Lee',
            'country':'China',
            'language':'Chinese',
        }
        response = self.client.post(reverse('user-register'), user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email='invalid_email').exists())
        mock_send_email.assert_not_called()

    def test_login_with_otp_success(self):
        user = User.objects.create(email='test@example.com')

        otp = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
        cache.set(f'otp:{user.email}', otp, timeout=900)

        data = {
            'email': 'test@example.com',
            'otp': otp,
        }
        response = self.client.post(reverse("user-login"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access_token', response.data['data'])
        self.assertIn('refresh_token', response.data['data'])

    def test_login_with_otp_invalid_otp(self):
        user = User.objects.create(email='test@example.com')

        otp = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
        cache.set(f'otp:{user.email}', otp, timeout=900)

        user_data = {
            'email': 'test@example.com',
            # Wrong OTP
            'otp': '1234',
        }
        response = self.client.post(reverse("user-login"), user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], 'invalid otp')

    def test_login_with_otp_expired_otp(self):
        user_data = {
            'email': 'test@example.com',
            'otp': '1234',
        }

        response = self.client.post(reverse("user-login"), user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], 'invalid otp')

    def test_login_with_otp_non_existent_user(self):
        otp = '1234'
        cache.set('otp:nonexistent@example.com', otp, timeout=900)

        data = {
            'email': 'nonexistent@example.com',
            'otp': otp,
        }
        response = self.client.post(reverse("user-login"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], 'invalid otp')

    def test_submit_review_authenticated(self):
        user_data = User.objects.create(
            email="tester@gmail.com",
            name='Harper Lee',
            country='China',
            language='Chinese',
        )

        company_data = Company.objects.create(
            company_name="Tech Solutions Inc.",
            industry="Information Technology",
            first_name="Alice",
            last_name="Johnson",
            job_title="CEO",
            work_email="alice.johnson@techsolutions.com",
            phone_number="+1234567890",
            country="USA",
            website="https://www.techsolutions.com",
            is_verified=True
        )

        valid_review_data = {
            'company': company_data.id,
            'rating': 4,
            'title': 'Great experience',
            'review_body': 'I had a wonderful time with this company.',
            'date_of_experience': '2023-01-01',
        }

        token = generate_access_token(user_data)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.post(reverse('submit-review'), valid_review_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)

        # Check if the review was actually created in the database
        self.assertTrue(Review.objects.filter(user=user_data, company=company_data).exists())
