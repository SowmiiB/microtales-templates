# Generated by Django 4.0.6 on 2024-04-22 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tales', '0004_remove_userprofile_saved_for_later_savedscribes'),
    ]

    operations = [
        migrations.AddField(
            model_name='scribes',
            name='likes',
            field=models.IntegerField(default=0),
        ),
    ]