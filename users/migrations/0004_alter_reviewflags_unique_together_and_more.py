# Generated by Django 5.1.1 on 2024-10-30 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_review_date_of_experience'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='reviewflags',
            unique_together={('review', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='reviewlikes',
            unique_together={('review', 'user')},
        ),
    ]
