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
    gender = models.CharField(max_length=50)
    education = models.CharField(max_length=100)
    age_range = models.CharField(max_length=50)
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


class Tests(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'tests'


class TagsList(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    level = models.CharField(max_length=200)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'tags_list'


class Questions(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=250)
    a = models.CharField(max_length=250)
    b = models.CharField(max_length=250)
    c = models.CharField(max_length=250)
    d = models.CharField(max_length=250)
    correct_answer = models.CharField(max_length=250)
    difficulty_level = models.CharField(max_length=100)
    tags = models.ForeignKey(TagsList, on_delete=models.CASCADE)

    class Meta:
        db_table = 'questions'


class Answers(models.Model):
    id = models.AutoField(primary_key=True)
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    answered = models.CharField(max_length=250)
    time_taken = models.FloatField()
    created_at = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=False)

    class Meta:
        db_table = 'answers'


class TestTagListLink(models.Model):
    id = models.AutoField(primary_key=True)
    tag = models.ForeignKey(TagsList, on_delete=models.CASCADE)
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    is_already_know = models.BooleanField(default=False)
    is_marked_as_checked = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'test_tag_list_link'
