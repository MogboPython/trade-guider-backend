import secrets
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APIClient

from users.models import User


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
