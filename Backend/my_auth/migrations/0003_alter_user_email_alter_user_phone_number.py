# Generated by Django 5.0.6 on 2024-07-23 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_auth', '0002_alter_user_is_official'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
