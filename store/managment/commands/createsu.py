from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

import os


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.filter(username=os.environ["DJANGO_SUPERUSER_USERNAME"]).exists():
            User.objects.create_superuser("admin", "admin@example.com", "adminpassword")
            self.stdout.write(self.style.SUCCESS("Superuser created"))
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists"))
