import shortuuid

from django.db import models

# Create your models here.

class Company(models.Model):
    id = models.CharField(max_length=27, unique=True, primary_key=True)

    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    work_email = models.EmailField(max_length=200)
    phone_number = models.CharField(max_length=15)
    country = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs) -> None:
        if not self.id:
            self.id = f'{shortuuid.uuid()}'

        return super().save(*args, **kwargs)

    @property
    def number_of_reviews(self):
        return self.reviews.count()

    @property
    def average_rating(self):
        return self.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0

# website
# company_name
# first_name
# last_name
# job_title
# work_email
# country
# phone_number
# stars --------
# number of reviews
# company ID
# excellent kinikan and kinikan based on the average reviews
# verification status
