import secrets
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APIClient

from users.models import User, Review
from common.helpers import generate_access_token
from business.models import Company


class TestUserRegisterView(TestCase):
    def setUp(self):
        self.user_register_url = reverse('user-register')
        self.client = APIClient()

    @patch('users.views.send_email')
    def test_register_user(self, mock_send_email):
        user_data = {
            'email': 'test-mogbo@gmail.com',
            'name': 'Harper Lee',
            'country': 'China',
            'language': 'Chinese',
        }
        response = self.client.post(self.user_register_url, user_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

        self.assertTrue(User.objects.filter(email=user_data['email']).exists())
        self.assertIsNotNone(cache.get(f"otp:{user_data['email']}"))
        mock_send_email.assert_called_once()

class TestViews(TestCase):
    # @classmethod
    # def setUpTestData(cls):
        # cls.valid_user_data = {
        #     'email': 'tester@gmail.com',
        #     'name': 'Harper Lee',
        #     'country': 'China',
        #     'language': 'Chinese',
        # }


    def setUp(self):
        self.company = Company.objects.create(
            company_name='Tech Solutions Inc.',
            category='Information Technology',
            first_name='Alice',
            last_name='Johnson',
            job_title='CEO',
            work_email='alice.johnson@techsolutions.com',
            phone_number='+1234567890',
            country='USA',
            website='https://www.techsolutions.com',
            is_verified=True,
        )

        self.valid_user_data = {
            'email': 'tester@gmail.com',
            'name': 'Harper Lee',
            'country': 'China',
            'language': 'Chinese',
        }

        self.user = User.objects.create(**self.valid_user_data)
        self.token = generate_access_token(self.user)

        self.other_user = User.objects.create(
            email='tester-email@gmail.com',
            name='Harper Lee',
            country='China',
            language='Chinese',
        )

        self.client = APIClient()

        self.user_register_url = reverse('user-register')
        self.user_login_url = reverse('user-login')
        self.submit_review_url = reverse('submit-review')
        self.update_profile_url = reverse('update-profile', kwargs={'user_id': self.user.id})
        self.other_user_url = reverse('update-profile', kwargs={'user_id': self.other_user.id})

        self.token = generate_access_token(self.user)


    def tearDown(self):
        User.objects.all().delete()

    def create_test_review_data(self):
        return {
            'company': self.company.id,
            'rating': 4,
            'title': 'Great experience',
            'review_body': 'I had a wonderful time with this company.',
        }

    @patch('users.views.send_email')
    def test_register_user_invalid_data(self, mock_send_email):
        invalid_data = self.valid_user_data.copy()
        invalid_data['email'] = 'invalid_email'

        response = self.client.post(self.user_register_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email='invalid_email').exists())
        mock_send_email.assert_not_called()

    def test_login_with_otp_success(self):
        otp = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
        cache.set(f'otp:{self.user.email}', otp, timeout=900)

        data = {
            'email': self.user.email,
            'otp': otp,
        }
        response = self.client.post(self.user_login_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access_token', response.data['data'])
        self.assertIn('refresh_token', response.data['data'])

    def test_login_with_otp_invalid_otp(self):
        otp = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
        cache.set(f'otp:{self.user.email}', otp, timeout=900)

        data = {
            'email': self.user.email,
            'otp': '1234',
        }
        response = self.client.post(self.user_login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], 'invalid otp')

    def test_login_with_otp_expired_otp(self):
        data = {
            'email': self.user.email,
            'otp': '1234',
        }
        response = self.client.post(self.user_login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], 'invalid otp')

    def test_login_with_otp_non_existent_user(self):
        otp = '1234'
        non_existent_email = 'nonexistent@example.com'
        cache.set(f'otp:{non_existent_email}', otp, timeout=900)

        data = {
            'email': non_existent_email,
            'otp': otp,
        }
        response = self.client.post(self.user_login_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error'], 'invalid otp')

    def test_submit_review_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        review_data = self.create_test_review_data()

        response = self.client.post(self.submit_review_url, review_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)

        self.assertTrue(Review.objects.filter(user=self.user, company=self.company).exists())

    def test_submit_review_unauthenticated(self):
        review_data = self.create_test_review_data()
        response = self.client.post(self.submit_review_url, review_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)

    def test_submit_review_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        invalid_review_data = self.create_test_review_data()
        invalid_review_data['rating'] = 6

        response = self.client.post(self.submit_review_url, invalid_review_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        data = {
            'name': 'updateduser',
            'country': 'Taiwan',
        }
        response = self.client.patch(self.update_profile_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data['data'])
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'updateduser')
        self.assertEqual(self.user.country, 'Taiwan')

    def test_update_user_profile_permission_denied(self):
        # another_user_data = {
        #     'email': 'tester-email@gmail.com',
        #     'name': 'Harper Lee',
        #     'country': 'China',
        #     'language': 'Chinese',
        # }
        # another_user_data.pop('id', None)
        # other_user = User.objects.create(**another_user_data)

        # other_user = User.objects.create(
        #     email = 'tester-email@gmail.com',
        #     name = 'Harper Lee',
        #     country = 'China',
        #     language = 'Chinese',
        # )
        # other_user_url = reverse('update-profile', kwargs={'user_id': other_user.id})

        data = {
            'name': 'should_fail',
            'country': 'Nigeria'
        }
        response = self.client.patch(self.other_user_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data['data'])
        self.assertEqual(response.data['detail'], "You don't have permission to update this profile.")

    # def test_update_user_profile_invalid_data(self):
    #     data = {
    #         'email': 'invalid_email',  # Invalid email format
    #     }
    #     response = self.client.patch(self.url, data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('email', response.data)  # Check for specific validation error

