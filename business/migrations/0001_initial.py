# Generated by Django 5.1.1 on 2024-10-02 11:57

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.CharField(max_length=27, primary_key=True, serialize=False, unique=True)),
                ('company_name', models.CharField(max_length=200)),
                ('industry', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('job_title', models.CharField(max_length=200)),
                ('work_email', models.EmailField(max_length=200)),
                ('phone_number', models.CharField(max_length=15)),
                ('country', models.CharField(max_length=100)),
                ('website', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_verified', models.BooleanField(default=False)),
            ],
        ),
    ]
