# Generated by Django 5.1.1 on 2024-11-16 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0004_alter_company_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='id',
            field=models.CharField(default='oHdNgT936sjo7PRNL6YsDF', max_length=27, primary_key=True, serialize=False, unique=True),
        ),
    ]
