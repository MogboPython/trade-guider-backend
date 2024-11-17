import shortuuid

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from business.models import Company


class User(models.Model):
    id = models.CharField(max_length=27, unique=True, primary_key=True, default=shortuuid.uuid)

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    # TODO: maybe pictures or not

    def __str__(self):
        return self.name

    @property
    def number_of_reviews(self):
        return self.reviews.count()

    @property
    def is_authenticated(self):
        return True


class Review(models.Model):
    id = models.CharField(max_length=27, unique=True, primary_key=True, default=shortuuid.uuid)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    review_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name}'s review of {self.company.company_name}"

    @property
    def number_of_likes(self):
        return self.likes.count()

    @property
    def number_of_flags(self):
        return self.flags.count()

class ReviewLikes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')

class ReviewFlags(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='flags')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')
