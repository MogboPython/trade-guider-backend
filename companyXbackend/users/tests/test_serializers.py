# from datetime import timedelta

import secrets

import shortuuid

from django.test import TestCase

# from django.utils import timezone
from rest_framework.test import APIRequestFactory

from users.models import User
from users.serializers import UserSerializer, LoginWithOTPSerializer


class LoginWithOTPSerializerTest(TestCase):
    def setUp(self) -> None:
        self.user_data = {
            'email':"tester@gmail.com",
            'otp':''.join([str(secrets.randbelow(10)) for _ in range(4)])
        }
        self.serializer_context = {'request': APIRequestFactory().post('/users/login/')}

    def test_login_serializer(self):
        serializer = LoginWithOTPSerializer(data=self.user_data, context=self.serializer_context)
        self.assertTrue(serializer.is_valid())

class UserSerializerTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email':"tester@gmail.com",
            'name':'Harper Lee',
            'country':'China',
            'language':'Chinese',
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
