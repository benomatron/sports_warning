from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


TIMEZONE_CHOICES = (
    ('US/Eastern', 'US/Eastern'),
    ('US/Central', 'US/Central'),
    ('US/Pacific', 'US/Pacific'),
    ('US/Mountain', 'US/Mountian'),
    ('US/Arizona', 'US/Arizona'),
    ('US/Michigan', 'US/Michigan'),
    ('US/Hawaii', 'US/Hawaii'),
    ('US/East-Indiana', 'US/East-Indiana'),
    ('US/Indiana-Starke', 'US/Indiana-Starke')
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email, email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        validate_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # Fields copied from Django 1.9's AbstractUser
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_superuser = models.BooleanField(
        default=False,
        help_text=_(
            'Designates that this user has all permissions without explicitly assigning them.'),
        verbose_name='superuser status')
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    phone_number = models.CharField(blank=True, max_length=20)
    country_code = models.CharField(blank=True, max_length=3, default='1')
    authy_user_id = models.CharField(blank=True, max_length=254)
    has_validated_phone = models.BooleanField(default=False)
    display_name = models.CharField(max_length=100, blank=True)
    time_zone = models.CharField(default='US/Eastern', choices=TIMEZONE_CHOICES, max_length=100)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        try:
            old_user = User.objects.get(id=self.id)
            if old_user.email != self.email:
                raise ValidationError('Email cannot be changed')
            if old_user.phone_number != self.phone_number or not self.phone_number:
                self.has_validated_phone = False
            if self.phone_number:
                # TODO: v2 - better phone validation
                try:
                    int_phone = int(self.phone_number)
                    if len(str(int_phone)) != 10:
                        self.phone_number = ''
                except ValueError:
                    self.phone_number = ''
            self.email = self.email.lower()
            validate_email(self.email)
        except User.DoesNotExist:
            pass
        if not self.pk:
            if not self.password:
                self.set_unusable_password()
            if not self.email:
                raise ValidationError('Email must be set')

        return super().save(*args, **kwargs)

    def get_full_name(self):
        """Required by AbstractBaseUser."""
        return self.display_name

    def get_short_name(self):
        return self.display_name.split()[0] if self.display_name else None
