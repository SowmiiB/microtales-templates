from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
import json


ROLE_CHOICES = [
    ('reader', "I'm a Reader"),
    ('writer', "I'm a Writer"),
]


class UserProfileManager(BaseUserManager):
    def create_user(self, email, username, phone, password=None, role=None, credentialId=None , **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, phone=phone, credentialId=credentialId,role=role, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, phone, password=None, role=None, credentialId=None , **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, phone, password, role, credentialId, **extra_fields)


class UserCredentials(AbstractBaseUser):
    credentialId = models.CharField(max_length=200,unique=True)
    email = models.EmailField(null=False)
    username = models.CharField(max_length=128)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    security_key = models.CharField(max_length=128,default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    userId = models.CharField(max_length=255,primary_key=True,db_column='userId')
    credentialId = models.ForeignKey('UserCredentials', on_delete=models.CASCADE, to_field='credentialId', db_column='credentialId')
    profileName = models.CharField(max_length=128,default='')
    about = models.TextField(default='')


class Scribes(models.Model):
    userId = models.ForeignKey('UserProfile', on_delete=models.SET_NULL, null=True, to_field='userId',db_column='userId')
    title = models.TextField()
    thumbnail = models.ImageField(upload_to='images/')
    ebook = models.FileField(upload_to='documents/')
    audio = models.FileField(upload_to='audio/')
    genre = models.CharField(max_length=128)
    language = models.CharField(max_length=128)
    likes = models.IntegerField(default=0)


class SavedScribes(models.Model):
    scribeId = models.ForeignKey('Scribes', on_delete=models.SET_NULL, null=True, to_field='id',db_column='scribeId')
    userId = models.ForeignKey('UserProfile', on_delete=models.SET_NULL, null=True, to_field='userId',db_column='userId')


class LikedScribes(models.Model):
    scribeId = models.ForeignKey('Scribes', on_delete=models.SET_NULL, null=True, to_field='id',db_column='scribeId')
    userId = models.ForeignKey('UserProfile', on_delete=models.SET_NULL, null=True, to_field='userId',db_column='userId')


class FavouriteAuthor(models.Model):
    scribeId = models.ForeignKey('Scribes', on_delete=models.SET_NULL, null=True, to_field='id', db_column='scribeId')
    readerId = models.ForeignKey('UserProfile', on_delete= models.CASCADE, to_field='userId', db_column='readerId')
    authorId = models.CharField(max_length=255,db_column='authorId')

    class Meta:
        unique_together = ('readerId', 'authorId')


class FrequencyAudio(models.Model):
    hz174 = models.FileField(upload_to='audio/')
    hz285 = models.FileField(upload_to='audio/')
    hz396 = models.FileField(upload_to='audio/')
    hz417 = models.FileField(upload_to='audio/')
    hz528 = models.FileField(upload_to='audio/')
    hz639 = models.FileField(upload_to='audio/')
    hz741 = models.FileField(upload_to='audio/')
    hz852 = models.FileField(upload_to='audio/')
    hz963 = models.FileField(upload_to='audio/')












