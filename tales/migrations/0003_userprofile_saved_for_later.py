# Generated by Django 4.0.6 on 2024-04-05 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tales', '0002_alter_usercredentials_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='saved_for_later',
            field=models.TextField(default='[]'),
        ),
    ]
