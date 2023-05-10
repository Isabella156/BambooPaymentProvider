from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
import hashlib
from django.db import models

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, nickname, password, name, user_id_number, user_phone, user_email, **extra_fields):
        if not user_phone:
            raise ValueError("The phone number is not given.")
        user_email = self.normalize_email(user_email)
        hash_id_number = hashlib.sha256(user_id_number.encode()).hexdigest()
        user = self.model(
            nickname=nickname,
            username=user_phone,
            name=name,
            user_id_number=hash_id_number,
            user_phone=user_phone,
            user_email=user_email,
        )
        user.is_active = True
        user.set_password(password)
        user.__dict__.update(extra_fields)
        user.save()
        return user

    # TODO: extra fields change
    def create_superuser(self, nickname, password, name, user_id_number, user_phone, user_email, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff = True")

        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser = True")
        return self.create_user(nickname, password, name, user_id_number, user_phone, user_email, **extra_fields)

class CustomUser(AbstractBaseUser):
    nickname = models.CharField(max_length=50, default='default_nickname', null=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=200, null=False)
    balance = models.IntegerField(default=0, null=False)
    name = models.CharField(max_length=50, null=False)
    user_id_number = models.CharField(
        max_length=200,
        validators=[RegexValidator(
            regex='^[1-9]\\d{5}(19|20)\\d{2}(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])\\d{3}[0-9xX]$',
            message='Please input right identification number'
        )], null=False
    )
    user_phone = PhoneNumberField(unique=True, null=False)
    user_email = models.EmailField(max_length=50, null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'user_phone'
    REQUIRED_FIELDS = ['nickname', 'password', 'name', 'user_id_number', 
    'user_email']

    objects = UserManager()

    def __str__(self):
        return str(self.username)

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True

class Statement(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=50)
    price = models.IntegerField()
    status = models.BooleanField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    def __str__(self):
        return self.user.username + str(self.description) + str(self.price)

class Invoice(models.Model):
    # Payment Provider
    PID = models.AutoField(primary_key=True, db_column='PID')
    # Airline
    AID = models.IntegerField()
    # Aggregator
    orderId = models.IntegerField()

    totalAmount = models.IntegerField()
    key = models.CharField(max_length=50)
    airline = models.CharField(max_length=50)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.airline + str(self.AID)
