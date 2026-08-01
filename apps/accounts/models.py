from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        username,
        password=None,
        first_name="",
        last_name="",
        password_is_hashed=False,
        **extra_fields,
    ):
        if not email:
            raise ValueError("Email is required.")

        if not username:
            raise ValueError("Username is required.")

        email = self.normalize_email(email)
        username = username.lower()

        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )
        if password_is_hashed:
            user.password = password
        else:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        username,
        password,
        first_name="",
        last_name="",
        **extra_fields,
    ):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)
        extra_fields.setdefault("is_super_admin", True)

        return self.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )


class User(AbstractBaseUser):
    email = models.EmailField(
        unique=True,
        max_length=255,
        db_index=True,
    )

    username = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        help_text="Unique public username used throughout Vurn.",
    )

    first_name = models.CharField(
        max_length=75,
    )

    last_name = models.CharField(
        max_length=75,
        blank=True,
    )

    avatar = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Public URL of the user's avatar.",
    )

    is_email_verified = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_super_admin = models.BooleanField(
        default=False,
    )

    last_login = models.DateTimeField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "username",
        "first_name",
    ]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"], name="idx_users_email"),
            models.Index(fields=["username"], name="idx_users_username"),
        ]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
        self.username = self.username.lower()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.username
