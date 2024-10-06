import shortuuid
from business.models import Company

from django.test import TestCase
from django.utils import timezone

from users.models import User, Review, ReviewFlags, ReviewLikes


class TestUserModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            id=f'user_{shortuuid.uuid()}',
            email="tester@gmail.com",
            name='Harper Lee',
            country='China',
            language='Chinese',
        )

        self.tech = Company.objects.create(
            id=f'{shortuuid.uuid()}',
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

    def test_user_creation(self):
        self.assertTrue(isinstance(self.user, User))
        self.assertEqual(self.user.email, 'tester@gmail.com')
        self.assertEqual(self.user.name, 'Harper Lee')
        self.assertTrue(self.user.id.startswith('user_'))
        self.assertEqual(self.user.country, 'China')
        self.assertEqual(self.user.language, 'Chinese')

    def test_user_str_method(self):
        self.assertEqual(str(self.user), 'Harper Lee')

    def test_user_reviews(self):
        self.assertEqual(self.user.number_of_reviews, 0)

        self.review = Review.objects.create(
            user=self.user,
            company=self.tech,
            rating=5,
            title="Excellent Service!",
            review_body="I had a fantastic experience with this company. \
                Their service was top-notch and the staff were very professional.",
            date_of_experience=timezone.now(),
        )

        self.assertEqual(self.user.number_of_reviews, 1)

class TestReviewModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            id=f'user_{shortuuid.uuid()}',
            email="tester@gmail.com",
            name='Harper Lee',
            country='China',
            language='Chinese',
        )

        self.tech = Company.objects.create(
            id=f'{shortuuid.uuid()}',
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

        self.review = Review.objects.create(
            user=self.user,
            company=self.tech,
            rating=5,
            title="Excellent Service!",
            review_body="I had a fantastic experience with this company. \
                Their service was top-notch and the staff were very professional.",
            date_of_experience='2024-01-15',
        )

    def test_review_creation(self):
        self.assertTrue(isinstance(self.review, Review))
        self.assertTrue(isinstance(self.review.user, User))
        self.assertTrue(isinstance(self.review.company, Company))
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.review_body, 'I had a fantastic experience with this company. \
                Their service was top-notch and the staff were very professional.')
        self.assertEqual(self.review.title, 'Excellent Service!')
        self.assertEqual(self.review.date_of_experience, '2024-01-15')

    def test_review_str_method(self):
        self.assertEqual(str(self.review), "Harper Lee's review of Tech Solutions Inc.")

    def test_review_likes(self):
        self.assertEqual(self.review.number_of_likes, 0)

        ReviewLikes.objects.create(
            user = self.user,
            review = self.review,
        )

        self.assertEqual(self.review.number_of_likes, 1)

    def test_review_flags(self):
        self.assertEqual(self.review.number_of_flags, 0)

        ReviewFlags.objects.create(
            user = self.user,
            review = self.review,
        )

        self.assertEqual(self.review.number_of_flags, 1)
