# Generated by Django 5.1.1 on 2024-11-16 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_reviewflags_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='id',
            field=models.CharField(default='dWSzZAzWgQN9ZmYHyr9MBJ', max_length=27, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.CharField(default='NdEhBXHdzTfiHADxAHh8K6', max_length=27, primary_key=True, serialize=False, unique=True),
        ),
    ]
