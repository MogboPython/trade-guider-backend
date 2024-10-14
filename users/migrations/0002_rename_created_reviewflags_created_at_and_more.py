# Generated by Django 5.1.1 on 2024-10-04 15:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reviewflags',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='reviewlikes',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RemoveField(
            model_name='review',
            name='invoice_number',
        ),
        migrations.AlterField(
            model_name='review',
            name='id',
            field=models.CharField(max_length=27, primary_key=True, serialize=False, unique=True),
        ),
    ]