from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    customer_type = models.CharField(max_length=50, choices=[('retail', 'Khách lẻ'), ('wholesale', 'Khách sỉ'), ('supplier', 'Nhà cung cấp')], default='retail')
    balance = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    join_date = models.DateField(auto_now_add=True)
    groups = models.ManyToManyField(Group, related_name="accounts_customuser_set", blank=True,help_text="The groups this user belongs to.",related_query_name="user")
    user_permissions = models.ManyToManyField(Permission, related_name="accounts_customuser_permissions_set", blank=True,help_text="Specific permissions for this user.",related_query_name="user",)

    def save(self, *args, **kwargs):
        if not self.pk:  # Ensure customer_type cannot be changed after creation
            self.customer_type = 'retail'
        super().save(*args, **kwargs)
