from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Role, UserRole

@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    if created:
        client_role, _ = Role.objects.get_or_create(name='Client')
        UserRole.objects.get_or_create(user=instance, role=client_role)
