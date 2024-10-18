import secrets
from datetime import date

import shortuuid

from django.test import TestCase

from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from users.models import User, Review
from business.models import Company
from users.serializers import UserSerializer, ReviewSerializer, LoginWithOTPSerializer


class LoginWithOTPSerializerTest(TestCase):
    def setUp(self) -> None:
        self.user_data = {'email': 'tester@gmail.com', 'otp': ''.join([str(secrets.randbelow(10)) for _ in range(4)])}
        self.serializer_context = {'request': APIRequestFactory().post('/users/login/')}

    def test_login_serializer(self):
        serializer = LoginWithOTPSerializer(data=self.user_data, context=self.serializer_context)
        self.assertTrue(serializer.is_valid())


class UserSerializerTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'tester@gmail.com',
            'name': 'Harper Lee',
            'country': 'China',
            'language': 'Chinese',
        }
        self.serializer_context = {'request': APIRequestFactory().post('/users/register/')}

    def test_user_serializer_create(self):
        serializer = UserSerializer(data=self.user_data, context=self.serializer_context)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertTrue(user.id.startswith('user_'))
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.name, self.user_data['name'])
        self.assertEqual(user.country, self.user_data['country'])
        self.assertEqual(user.language, self.user_data['language'])

    def test_user_serializer_read_only_fields(self):
        user = User.objects.create(id=f'user_{shortuuid.uuid()}', **self.user_data)
        serializer = UserSerializer(user)
        data = serializer.data

        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('is_verified', data)

    # def test_book_serializer_update(self):
    #     book = Book.objects.create(id=f'book_{shortuuid.uuid()}', added_by=self.user_id, **self.book_data)
    #     updated_data = {
    #         'title': 'Updated Title',
    #         'author': 'Updated Author',
    #     }
    #     serializer = BookSerializer(book, data=updated_data, partial=True)
    #     self.assertTrue(serializer.is_valid())
    #     updated_book = serializer.save()

    #     self.assertEqual(updated_book.title, 'Updated Title')
    #     self.assertEqual(updated_book.author, 'Updated Author')
    #     self.assertEqual(updated_book.id, book.id)
    #     self.assertEqual(updated_book.added_by, book.added_by)


class ReviewSerializerTestCase(TestCase):
    def setUp(self):
        self.user_data = User.objects.create(
            email='tester@gmail.com',
            name='Harper Lee',
            country='China',
            language='Chinese',
        )
        self.company_data = Company.objects.create(
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

        self.review_data = {
            'company': self.company_data.id,
            'rating': 4,
            'title': 'Great experience',
            'review_body': 'I had a wonderful time with this company.',
        }

        self.factory = APIRequestFactory()
        self.serializer_context = {
            'request': Request(self.factory.get('/')),
        }
        self.serializer_context['request'].user = self.user_data

    def test_serialize_review(self):
        review_data = {
            'company': self.company_data,
            'rating': 4,
            'title': 'Great experience',
            'review_body': 'I had a wonderful time with this company.',
        }

        review = Review.objects.create(user=self.user_data, **review_data)
        serializer = ReviewSerializer(review)
        data = serializer.data

        self.assertEqual(data['rating'], self.review_data['rating'])
        self.assertEqual(data['title'], self.review_data['title'])
        self.assertEqual(data['review_body'], self.review_data['review_body'])

        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

    def test_review_deserializer(self):
        serializer = ReviewSerializer(data=self.review_data, context=self.serializer_context)
        self.assertTrue(serializer.is_valid())
        review = serializer.save()

        self.assertTrue(review.user, self.user_data)
        self.assertEqual(review.company, self.company_data)
        self.assertEqual(review.rating, self.review_data['rating'])
        self.assertEqual(review.title, self.review_data['title'])
        self.assertEqual(review.review_body, self.review_data['review_body'])

    def test_deserialize_invalid_data(self):
        invalid_data = self.review_data.copy()
        invalid_data['rating'] = 6
        serializer = ReviewSerializer(data=invalid_data, context=self.serializer_context)
        self.assertFalse(serializer.is_valid())
        self.assertIn('rating', serializer.errors)

    def test_read_only_fields(self):
        another_user = User.objects.create(
            id=f'user_{shortuuid.uuid()}',
            email='tester2@gmail.com',
            name='Mogbo Lee',
            country='Australia',
            language='English',
        )

        serializer = ReviewSerializer(data=self.review_data, context=self.serializer_context)
        self.assertTrue(serializer.is_valid())
        review = serializer.save()

        updated_data = self.review_data.copy()
        updated_data['user'] = UserSerializer(another_user).data
        updated_data['id'] = 999
        updated_data['created_at'] = '2022-01-01T00:00:00Z'
        updated_data['updated_at'] = '2022-01-01T00:00:00Z'

        serializer = ReviewSerializer(instance=review, data=updated_data, context=self.serializer_context)
        self.assertTrue(serializer.is_valid())
        updated_review = serializer.save()

        self.assertEqual(updated_review.user, self.user_data)
        self.assertNotEqual(updated_review.user, another_user)
        self.assertNotEqual(updated_review.id, 999)
        self.assertNotEqual(updated_review.created_at.isoformat(), '2022-01-01T00:00:00+00:00')
        self.assertNotEqual(updated_review.updated_at.isoformat(), '2022-01-01T00:00:00+00:00')
