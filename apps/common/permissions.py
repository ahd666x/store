from django.contrib.auth.models import AnonymousUser


def is_production_staff(user):
    if isinstance(user, AnonymousUser):
        return False
    return user.is_staff or user.is_superuser or hasattr(user, 'worker_profile')
