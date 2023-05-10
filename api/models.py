from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password=password, **extra_fields)


class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=75)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']
    objects = MyUserManager()

    @classmethod
    def email_exists(cls, email):
        """
        Check if an email address exists in the User model.
        """

        return cls.objects.filter(email=email).exists()

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.email


class Questions(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=250)
    a = models.CharField(max_length=250)
    b = models.CharField(max_length=250)
    c = models.CharField(max_length=250)
    d = models.CharField(max_length=250)
    correct_answer = models.CharField(max_length=250)
    difficulty_level = models.CharField(max_length=100)
    tags = models.CharField(max_length=100)

    class Meta:
        db_table = 'questions'



class Answers(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Questions,models.CASCADE)
    user = models.ForeignKey(User,models.CASCADE)
    answered = models.CharField(max_length=250)
    time_taken = models.FloatField()
    created_at = models.DateField(auto_now_add=True)

