import shortuuid

from django.db import models


class Company(models.Model):
    id = models.CharField(max_length=27, unique=True, primary_key=True)

    company_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=200, default='')
    first_name = models.CharField(max_length=200, default='')
    last_name = models.CharField(max_length=200, default='')
    job_title = models.CharField(max_length=200, default='')
    work_email = models.EmailField(max_length=200, default='')
    phone_number = models.CharField(max_length=15, default='')
    country = models.CharField(max_length=100)
    website = models.CharField(blank=True,  unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    is_claimed = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs) -> None:
        if not self.id:
            self.id = f'{shortuuid.uuid()}'

        if self.work_email:
            self.is_claimed = True

        return super().save(*args, **kwargs)

    @property
    def number_of_reviews(self):
        return self.reviews.count()

    @property
    def average_rating(self):
        return self.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0

    @property
    def is_authenticated(self):
        return True

# class CompanyInfo(models.Model):
#     about = models.TextField()


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
