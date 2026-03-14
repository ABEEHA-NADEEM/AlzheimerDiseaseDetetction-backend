from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('doctor',  'Doctor'),
        ('patient', 'Patient'),
        ('admin',   'Admin'),
    ]

    role           = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    is_approved    = models.BooleanField(default=False)  # doctors need approval
    specialization = models.CharField(max_length=100, blank=True)  # doctors only
    phone          = models.CharField(max_length=20, blank=True)
    date_of_birth  = models.DateField(null=True, blank=True)        # patients only
    created_at     = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Patients & admins are auto-approved, doctors need manual approval
        if self.role in ['patient', 'admin']:
            self.is_approved = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"